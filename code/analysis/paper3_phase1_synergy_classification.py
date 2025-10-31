#!/usr/bin/env python3
"""
Paper 3 Phase 1: Synergy Classification Analysis

Analyzes 6 factorial experiments (C255-C260) to classify mechanism interactions:
- H1×H2, H1×H4, H1×H5, H2×H4, H2×H5, H4×H5
- Determines SYNERGISTIC, ANTAGONISTIC, or ADDITIVE classification
- Calculates synergy magnitudes and fold changes
- Generates results tables for Paper 3 manuscript

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


class SynergyClassifier:
    """
    Classify mechanism interactions from factorial experiments.

    For each 2×2 factorial:
    - Calculate additive prediction: Pred(AB) = A + B - OFF
    - Measure actual combined effect: Obs(AB)
    - Synergy = Obs(AB) - Pred(AB)
    - Classify: SYNERGISTIC (>10% above), ANTAGONISTIC (<-10% below), ADDITIVE (within ±10%)
    """

    def __init__(self, experiment_data: Dict[str, Path]):
        """
        Initialize classifier with experiment result files.

        Args:
            experiment_data: Dict mapping pair IDs to result JSON paths
                           e.g., {'H1xH2': Path('cycle255_results.json'), ...}
        """
        self.experiment_data = experiment_data
        self.experiments = {}
        self.load_experiments()

    def load_experiments(self):
        """Load experiment data from JSON files."""
        for pair_id, path in self.experiment_data.items():
            if not path.exists():
                print(f"Warning: {pair_id} results not found at {path}", file=sys.stderr)
                continue

            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.experiments[pair_id] = data
                    print(f"Loaded {pair_id}: {len(data.get('results', []))} conditions")
            except Exception as e:
                print(f"Error loading {pair_id}: {e}", file=sys.stderr)

    def classify_synergy(self, pair_id: str, metric: str = 'mean_population') -> Dict:
        """
        Classify synergy for a single factorial pair.

        Args:
            pair_id: Experiment pair ID (e.g., 'H1xH2')
            metric: Performance metric to analyze (default: 'mean_population')

        Returns:
            Dict with classification results
        """
        if pair_id not in self.experiments:
            return {'error': f'{pair_id} not loaded'}

        data = self.experiments[pair_id]
        results = data.get('results', [])

        # Need exactly 4 conditions for 2×2 factorial
        if len(results) != 4:
            return {'error': f'{pair_id} has {len(results)} conditions, expected 4'}

        # Extract conditions
        conditions = {r['condition_name']: r for r in results}

        # Verify factorial structure
        required = ['OFF-OFF', 'ON-OFF', 'OFF-ON', 'ON-ON']
        if not all(cond in conditions for cond in required):
            return {'error': f'{pair_id} missing required conditions: {required}'}

        # Extract metric values (take mean if list, use directly if scalar)
        def extract_value(condition_data):
            val = condition_data.get(metric, 0)
            return np.mean(val) if isinstance(val, list) else val

        off_off = extract_value(conditions['OFF-OFF'])
        on_off = extract_value(conditions['ON-OFF'])
        off_on = extract_value(conditions['OFF-ON'])
        on_on = extract_value(conditions['ON-ON'])

        # Additive prediction: ON-ON_pred = ON-OFF + OFF-ON - OFF-OFF
        predicted = on_off + off_on - off_off
        observed = on_on
        synergy = observed - predicted

        # Relative synergy (percentage of baseline)
        synergy_pct = (synergy / off_off * 100) if off_off > 0 else 0

        # Classification thresholds
        if abs(synergy_pct) < 10:
            classification = 'ADDITIVE'
            interpretation = 'Mechanisms combine additively (within ±10% of prediction)'
        elif synergy_pct > 0:
            classification = 'SYNERGISTIC'
            interpretation = 'Mechanisms cooperate (better than additive)'
        else:
            classification = 'ANTAGONISTIC'
            interpretation = 'Mechanisms interfere (worse than additive)'

        # Fold changes
        fold_change_off = on_off / off_off if off_off > 0 else 0
        fold_change_on = off_on / off_off if off_off > 0 else 0
        fold_change_combined_observed = on_on / off_off if off_off > 0 else 0
        fold_change_combined_predicted = predicted / off_off if off_off > 0 else 0

        return {
            'pair_id': pair_id,
            'metric': metric,
            'conditions': {
                'OFF-OFF': off_off,
                'ON-OFF': on_off,
                'OFF-ON': off_on,
                'ON-ON': on_on
            },
            'fold_changes': {
                'mechanism_a_alone': fold_change_off,
                'mechanism_b_alone': fold_change_on,
                'combined_observed': fold_change_combined_observed,
                'combined_predicted': fold_change_combined_predicted
            },
            'synergy': {
                'predicted_combined': predicted,
                'observed_combined': observed,
                'synergy_absolute': synergy,
                'synergy_percent': synergy_pct
            },
            'classification': classification,
            'interpretation': interpretation
        }

    def classify_all_pairs(self, metric: str = 'mean_population') -> Dict:
        """Classify synergy for all loaded pairs."""
        results = {}
        for pair_id in self.experiments.keys():
            results[pair_id] = self.classify_synergy(pair_id, metric)
        return results

    def generate_classification_table(self, metric: str = 'mean_population') -> str:
        """Generate human-readable classification table."""
        classifications = self.classify_all_pairs(metric)

        lines = []
        lines.append("=" * 80)
        lines.append("PAPER 3 PHASE 1: SYNERGY CLASSIFICATION")
        lines.append("=" * 80)
        lines.append("")

        # Summary table
        lines.append("CLASSIFICATION SUMMARY")
        lines.append("-" * 80)
        lines.append(f"{'Pair':<10} {'Class':<15} {'Synergy %':<12} {'Obs Fold':<12} {'Pred Fold':<12}")
        lines.append("-" * 80)

        for pair_id, result in classifications.items():
            if 'error' in result:
                lines.append(f"{pair_id:<10} ERROR: {result['error']}")
                continue

            synergy_pct = result['synergy']['synergy_percent']
            obs_fold = result['fold_changes']['combined_observed']
            pred_fold = result['fold_changes']['combined_predicted']
            classification = result['classification']

            lines.append(f"{pair_id:<10} {classification:<15} {synergy_pct:>10.2f}% "
                        f"{obs_fold:>10.2f}× {pred_fold:>10.2f}×")

        lines.append("")

        # Detailed results per pair
        lines.append("DETAILED CLASSIFICATION RESULTS")
        lines.append("-" * 80)

        for pair_id, result in classifications.items():
            if 'error' in result:
                continue

            lines.append("")
            lines.append(f"Pair: {pair_id}")
            lines.append(f"  Classification: {result['classification']}")
            lines.append(f"  Interpretation: {result['interpretation']}")
            lines.append("")
            lines.append("  Conditions:")
            lines.append(f"    OFF-OFF: {result['conditions']['OFF-OFF']:.2f}")
            lines.append(f"    ON-OFF:  {result['conditions']['ON-OFF']:.2f} "
                        f"({result['fold_changes']['mechanism_a_alone']:.2f}× vs OFF-OFF)")
            lines.append(f"    OFF-ON:  {result['conditions']['OFF-ON']:.2f} "
                        f"({result['fold_changes']['mechanism_b_alone']:.2f}× vs OFF-OFF)")
            lines.append(f"    ON-ON:   {result['conditions']['ON-ON']:.2f} "
                        f"({result['fold_changes']['combined_observed']:.2f}× vs OFF-OFF)")
            lines.append("")
            lines.append("  Synergy Analysis:")
            lines.append(f"    Predicted (additive): {result['synergy']['predicted_combined']:.2f} "
                        f"({result['fold_changes']['combined_predicted']:.2f}× vs OFF-OFF)")
            lines.append(f"    Observed (actual):    {result['synergy']['observed_combined']:.2f} "
                        f"({result['fold_changes']['combined_observed']:.2f}× vs OFF-OFF)")
            lines.append(f"    Synergy:              {result['synergy']['synergy_absolute']:.2f} "
                        f"({result['synergy']['synergy_percent']:.2f}% vs OFF-OFF)")
            lines.append("-" * 80)

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def export_results_json(self, output_path: Path, metric: str = 'mean_population'):
        """Export classification results as JSON for programmatic use."""
        classifications = self.classify_all_pairs(metric)

        with open(output_path, 'w') as f:
            json.dump(classifications, f, indent=2)

        print(f"Results exported to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Classify synergy for Paper 3 factorial experiments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify all 6 pairs (C255-C260)
  python paper3_phase1_synergy_classification.py \\
      --pairs \\
          H1xH2=data/results/cycle255_results.json \\
          H1xH4=data/results/cycle256_results.json \\
          H1xH5=data/results/cycle257_results.json \\
          H2xH4=data/results/cycle258_results.json \\
          H2xH5=data/results/cycle259_results.json \\
          H4xH5=data/results/cycle260_results.json

  # Export as JSON
  python paper3_phase1_synergy_classification.py \\
      --pairs H1xH2=cycle255_results.json H1xH4=cycle256_results.json \\
      --json paper3_phase1_results.json

  # Use custom metric (e.g., composition_depth)
  python paper3_phase1_synergy_classification.py \\
      --pairs H1xH2=cycle255_results.json \\
      --metric composition_depth
        """
    )

    parser.add_argument('--pairs', nargs='+', required=True,
                       help='Factorial pairs in format: ID=path (e.g., H1xH2=results.json)')
    parser.add_argument('--metric', type=str, default='mean_population',
                       help='Metric to analyze (default: mean_population)')
    parser.add_argument('--json', type=Path, default=None,
                       help='Export results as JSON to specified path')

    args = parser.parse_args()

    # Parse pair specifications
    experiment_data = {}
    for pair_spec in args.pairs:
        if '=' not in pair_spec:
            print(f"Error: Invalid pair spec '{pair_spec}'. Use format: ID=path", file=sys.stderr)
            sys.exit(1)

        pair_id, pair_path = pair_spec.split('=', 1)
        experiment_data[pair_id] = Path(pair_path)

    # Create classifier
    classifier = SynergyClassifier(experiment_data)

    if len(classifier.experiments) == 0:
        print("Error: No experiments loaded successfully", file=sys.stderr)
        sys.exit(1)

    # Generate output
    if args.json:
        classifier.export_results_json(args.json, args.metric)
    else:
        print(classifier.generate_classification_table(args.metric))


if __name__ == '__main__':
    main()
