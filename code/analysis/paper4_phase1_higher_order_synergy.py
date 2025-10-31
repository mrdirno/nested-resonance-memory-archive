#!/usr/bin/env python3
"""
Paper 4 Phase 1: Higher-Order Synergy Analysis

Analyzes 3-way and 4-way factorial experiments (C262-C263) to detect emergent
synergies beyond pairwise predictions:
- 3-way interactions: H1×H2×H4, H1×H2×H5, H1×H4×H5, H2×H4×H5 (4 combinations, 32 conditions)
- 4-way interaction: H1×H2×H4×H5 (1 combination, 16 conditions)
- Tests if pairwise models (Paper 3) predict higher-order behavior
- Classifies emergent synergies (>10%), antagonisms (<-10%), or additive (±10%)

Designed for immediate execution when C262-C263 complete (zero-delay finalization).
Requires Paper 3 pairwise results as baseline predictions.

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


class HigherOrderSynergyAnalyzer:
    """
    Analyze 3-way and 4-way mechanism interactions.

    For 3-way factorial (e.g., H1×H2×H4):
    - 2³ = 8 conditions (OFF-OFF-OFF through ON-ON-ON)
    - Predict ON-ON-ON from pairwise model (Paper 3 results)
    - 3-way synergy = Observed(ON-ON-ON) - Predicted_from_pairwise

    For 4-way factorial (H1×H2×H4×H5):
    - 2⁴ = 16 conditions (OFF-OFF-OFF-OFF through ON-ON-ON-ON)
    - Predict ON-ON-ON-ON from pairwise + 3-way models
    - 4-way synergy = Observed(ON-ON-ON-ON) - Predicted_from_lower_orders

    Classification:
    - EMERGENT SYNERGISTIC: synergy > +10%
    - EMERGENT ANTAGONISTIC: synergy < -10%
    - PAIRWISE MODEL GENERALIZES: |synergy| ≤ 10%
    """

    def __init__(self, pairwise_results_path: Path):
        """
        Initialize analyzer with Paper 3 pairwise results.

        Args:
            pairwise_results_path: Path to Paper 3 Phase 1 results JSON
        """
        self.pairwise_results = self._load_pairwise_results(pairwise_results_path)

    def _load_pairwise_results(self, path: Path) -> Dict:
        """Load Paper 3 pairwise synergy results."""
        if not path.exists():
            raise FileNotFoundError(f"Paper 3 results not found: {path}")

        try:
            with open(path, 'r') as f:
                data = json.load(f)
                print(f"Loaded Paper 3 pairwise results: {len(data)} pairs")
                return data
        except Exception as e:
            raise RuntimeError(f"Failed to load Paper 3 results: {e}")

    def analyze_3way_interaction(
        self,
        factorial_data_path: Path,
        combination: str,  # e.g., "H1xH2xH4"
        metric: str = 'mean_population'
    ) -> Dict:
        """
        Analyze 3-way interaction from 2³ factorial experiment.

        Args:
            factorial_data_path: Path to experiment results JSON (8 conditions)
            combination: Mechanism combination ID (e.g., "H1xH2xH4")
            metric: Performance metric to analyze

        Returns:
            Dict with 3-way synergy analysis results
        """
        # Load 3-way factorial data
        if not factorial_data_path.exists():
            return {'error': f'Factorial data not found: {factorial_data_path}'}

        try:
            with open(factorial_data_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return {'error': f'Failed to load factorial data: {e}'}

        results = data.get('results', [])
        if len(results) != 8:
            return {'error': f'Expected 8 conditions for 3-way factorial, got {len(results)}'}

        # Extract conditions
        conditions = {r['condition_name']: r for r in results}

        # Verify factorial structure
        required = [
            'OFF-OFF-OFF', 'ON-OFF-OFF', 'OFF-ON-OFF', 'OFF-OFF-ON',
            'ON-ON-OFF', 'ON-OFF-ON', 'OFF-ON-ON', 'ON-ON-ON'
        ]
        if not all(cond in conditions for cond in required):
            return {'error': f'Missing required conditions: {required}'}

        # Extract metric values
        def extract_value(condition_data):
            val = condition_data.get(metric, 0)
            return np.mean(val) if isinstance(val, list) else val

        # All 8 condition values
        condition_values = {cond: extract_value(conditions[cond]) for cond in required}

        # Parse mechanism IDs from combination (e.g., "H1xH2xH4" -> ["H1", "H2", "H4"])
        mechanisms = combination.split('x')
        if len(mechanisms) != 3:
            return {'error': f'Invalid 3-way combination: {combination}'}

        # Calculate pairwise prediction
        baseline = condition_values['OFF-OFF-OFF']

        # 1st order effects (main effects)
        # For H1xH2xH4: H1_effect = (ON-OFF-OFF - OFF-OFF-OFF)
        mech_a_effect = condition_values['ON-OFF-OFF'] - baseline
        mech_b_effect = condition_values['OFF-ON-OFF'] - baseline
        mech_c_effect = condition_values['OFF-OFF-ON'] - baseline

        # 2nd order effects (pairwise synergies from Paper 3)
        # Need to extract synergies for: H1xH2, H1xH4, H2xH4 (for H1xH2xH4 example)
        pair_ab = f"{mechanisms[0]}x{mechanisms[1]}"  # H1xH2
        pair_ac = f"{mechanisms[0]}x{mechanisms[2]}"  # H1xH4
        pair_bc = f"{mechanisms[1]}x{mechanisms[2]}"  # H2xH4

        # Extract pairwise synergies (if available)
        synergy_ab = self._get_pairwise_synergy(pair_ab, metric)
        synergy_ac = self._get_pairwise_synergy(pair_ac, metric)
        synergy_bc = self._get_pairwise_synergy(pair_bc, metric)

        # Predicted from pairwise model
        predicted_from_pairwise = (
            baseline +
            mech_a_effect + mech_b_effect + mech_c_effect +  # 1st order
            synergy_ab + synergy_ac + synergy_bc  # 2nd order (pairwise synergies)
        )

        # Observed (actual measurement)
        observed = condition_values['ON-ON-ON']

        # 3-way synergy
        synergy_3way = observed - predicted_from_pairwise
        synergy_3way_pct = (synergy_3way / baseline * 100) if baseline > 0 else 0

        # Classification
        if abs(synergy_3way_pct) < 10:
            classification = 'PAIRWISE MODEL GENERALIZES'
            interpretation = 'Pairwise interactions sufficient (3-way synergy within ±10%)'
        elif synergy_3way_pct > 0:
            classification = 'EMERGENT SYNERGISTIC'
            interpretation = 'Positive 3-way synergy beyond pairwise prediction (>10%)'
        else:
            classification = 'EMERGENT ANTAGONISTIC'
            interpretation = 'Negative 3-way interference beyond pairwise prediction (<-10%)'

        return {
            'combination': combination,
            'mechanisms': mechanisms,
            'metric': metric,
            'condition_values': condition_values,
            'baseline': baseline,
            'first_order_effects': {
                mechanisms[0]: mech_a_effect,
                mechanisms[1]: mech_b_effect,
                mechanisms[2]: mech_c_effect
            },
            'second_order_synergies': {
                pair_ab: synergy_ab,
                pair_ac: synergy_ac,
                pair_bc: synergy_bc
            },
            'prediction': {
                'from_pairwise': predicted_from_pairwise,
                'observed': observed,
                'synergy_3way_absolute': synergy_3way,
                'synergy_3way_percent': synergy_3way_pct
            },
            'classification': classification,
            'interpretation': interpretation
        }

    def analyze_4way_interaction(
        self,
        factorial_data_path: Path,
        three_way_results: Dict,  # Results from analyze_3way_interaction for all 4 combinations
        combination: str = "H1xH2xH4xH5",
        metric: str = 'mean_population'
    ) -> Dict:
        """
        Analyze 4-way interaction from 2⁴ factorial experiment.

        Args:
            factorial_data_path: Path to experiment results JSON (16 conditions)
            three_way_results: Dict mapping 3-way combinations to their synergy results
            combination: Mechanism combination ID (must be "H1xH2xH4xH5")
            metric: Performance metric to analyze

        Returns:
            Dict with 4-way synergy analysis results
        """
        # Load 4-way factorial data
        if not factorial_data_path.exists():
            return {'error': f'Factorial data not found: {factorial_data_path}'}

        try:
            with open(factorial_data_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return {'error': f'Failed to load factorial data: {e}'}

        results = data.get('results', [])
        if len(results) != 16:
            return {'error': f'Expected 16 conditions for 4-way factorial, got {len(results)}'}

        # Extract all 16 condition values
        conditions = {r['condition_name']: r for r in results}

        def extract_value(condition_data):
            val = condition_data.get(metric, 0)
            return np.mean(val) if isinstance(val, list) else val

        # Baseline
        baseline = extract_value(conditions['OFF-OFF-OFF-OFF'])

        # Mechanisms
        mechanisms = ["H1", "H2", "H4", "H5"]

        # 1st order effects (4 main effects)
        h1_effect = extract_value(conditions['ON-OFF-OFF-OFF']) - baseline
        h2_effect = extract_value(conditions['OFF-ON-OFF-OFF']) - baseline
        h4_effect = extract_value(conditions['OFF-OFF-ON-OFF']) - baseline
        h5_effect = extract_value(conditions['OFF-OFF-OFF-ON']) - baseline

        # 2nd order effects (6 pairwise synergies from Paper 3)
        synergy_h1xh2 = self._get_pairwise_synergy("H1xH2", metric)
        synergy_h1xh4 = self._get_pairwise_synergy("H1xH4", metric)
        synergy_h1xh5 = self._get_pairwise_synergy("H1xH5", metric)
        synergy_h2xh4 = self._get_pairwise_synergy("H2xH4", metric)
        synergy_h2xh5 = self._get_pairwise_synergy("H2xH5", metric)
        synergy_h4xh5 = self._get_pairwise_synergy("H4xH5", metric)

        # 3rd order effects (4 3-way synergies)
        synergy_3way_h1h2h4 = three_way_results.get("H1xH2xH4", {}).get('prediction', {}).get('synergy_3way_absolute', 0)
        synergy_3way_h1h2h5 = three_way_results.get("H1xH2xH5", {}).get('prediction', {}).get('synergy_3way_absolute', 0)
        synergy_3way_h1h4h5 = three_way_results.get("H1xH4xH5", {}).get('prediction', {}).get('synergy_3way_absolute', 0)
        synergy_3way_h2h4h5 = three_way_results.get("H2xH4xH5", {}).get('prediction', {}).get('synergy_3way_absolute', 0)

        # Predicted from lower orders
        predicted = (
            baseline +
            h1_effect + h2_effect + h4_effect + h5_effect +  # 1st order
            synergy_h1xh2 + synergy_h1xh4 + synergy_h1xh5 +  # 2nd order
            synergy_h2xh4 + synergy_h2xh5 + synergy_h4xh5 +
            synergy_3way_h1h2h4 + synergy_3way_h1h2h5 +  # 3rd order
            synergy_3way_h1h4h5 + synergy_3way_h2h4h5
        )

        # Observed
        observed = extract_value(conditions['ON-ON-ON-ON'])

        # 4-way synergy
        synergy_4way = observed - predicted
        synergy_4way_pct = (synergy_4way / baseline * 100) if baseline > 0 else 0

        # Classification
        if abs(synergy_4way_pct) < 10:
            classification = 'LOWER-ORDER MODELS GENERALIZE'
            interpretation = 'Pairwise + 3-way models sufficient (4-way synergy within ±10%)'
        elif synergy_4way_pct > 0:
            classification = 'EMERGENT 4-WAY SYNERGISTIC'
            interpretation = 'Qualitative shift at 4-mechanism combination (>10% synergy)'
        else:
            classification = 'EMERGENT 4-WAY ANTAGONISTIC'
            interpretation = 'Qualitative interference at 4-mechanism combination (<-10%)'

        return {
            'combination': combination,
            'mechanisms': mechanisms,
            'metric': metric,
            'baseline': baseline,
            'first_order_effects': {
                'H1': h1_effect,
                'H2': h2_effect,
                'H4': h4_effect,
                'H5': h5_effect
            },
            'second_order_synergies': {
                'H1xH2': synergy_h1xh2,
                'H1xH4': synergy_h1xh4,
                'H1xH5': synergy_h1xh5,
                'H2xH4': synergy_h2xh4,
                'H2xH5': synergy_h2xh5,
                'H4xH5': synergy_h4xh5
            },
            'third_order_synergies': {
                'H1xH2xH4': synergy_3way_h1h2h4,
                'H1xH2xH5': synergy_3way_h1h2h5,
                'H1xH4xH5': synergy_3way_h1h4h5,
                'H2xH4xH5': synergy_3way_h2h4h5
            },
            'prediction': {
                'from_lower_orders': predicted,
                'observed': observed,
                'synergy_4way_absolute': synergy_4way,
                'synergy_4way_percent': synergy_4way_pct
            },
            'classification': classification,
            'interpretation': interpretation
        }

    def _get_pairwise_synergy(self, pair_id: str, metric: str) -> float:
        """
        Extract pairwise synergy from Paper 3 results.

        Args:
            pair_id: Pair ID (e.g., "H1xH2")
            metric: Metric name

        Returns:
            Synergy value (absolute, not percentage)
        """
        if pair_id not in self.pairwise_results:
            print(f"Warning: Pairwise result for {pair_id} not found", file=sys.stderr)
            return 0.0

        pair_data = self.pairwise_results[pair_id]

        if 'error' in pair_data:
            print(f"Warning: Error in {pair_id} results: {pair_data['error']}", file=sys.stderr)
            return 0.0

        synergy_info = pair_data.get('synergy', {})
        return synergy_info.get('synergy_absolute', 0.0)

    def generate_summary_table(self, results_3way: Dict, results_4way: Optional[Dict] = None) -> str:
        """Generate human-readable summary table."""
        lines = []
        lines.append("=" * 80)
        lines.append("PAPER 4 PHASE 1: HIGHER-ORDER SYNERGY ANALYSIS")
        lines.append("=" * 80)
        lines.append("")

        # 3-way results
        if results_3way:
            lines.append("3-WAY INTERACTION SUMMARY")
            lines.append("-" * 80)
            lines.append(f"{'Combination':<15} {'Classification':<30} {'Synergy %':<12}")
            lines.append("-" * 80)

            for combo, result in results_3way.items():
                if 'error' in result:
                    lines.append(f"{combo:<15} ERROR: {result['error']}")
                    continue

                classification = result['classification']
                synergy_pct = result['prediction']['synergy_3way_percent']

                lines.append(f"{combo:<15} {classification:<30} {synergy_pct:>10.2f}%")

            lines.append("")

        # 4-way results
        if results_4way and 'error' not in results_4way:
            lines.append("4-WAY INTERACTION SUMMARY")
            lines.append("-" * 80)

            combo = results_4way['combination']
            classification = results_4way['classification']
            synergy_pct = results_4way['prediction']['synergy_4way_percent']

            lines.append(f"Combination: {combo}")
            lines.append(f"Classification: {classification}")
            lines.append(f"4-way Synergy: {synergy_pct:.2f}%")
            lines.append(f"Interpretation: {results_4way['interpretation']}")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze higher-order mechanism interactions (Paper 4)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze 3-way interaction H1×H2×H4
  python paper4_phase1_higher_order_synergy.py \\
      --three-way \\
      --pairwise-results paper3_phase1_results.json \\
      --factorial-data data/results/cycle262_h1h2h4_3way.json \\
      --combination H1xH2xH4 \\
      --output paper4_phase1_H1xH2xH4_3way.json

  # Analyze 4-way interaction H1×H2×H4×H5
  python paper4_phase1_higher_order_synergy.py \\
      --four-way \\
      --pairwise-results paper3_phase1_results.json \\
      --three-way-results paper4_phase1_3way_combined.json \\
      --factorial-data data/results/cycle263_h1h2h4h5_4way.json \\
      --output paper4_phase1_4way.json
        """
    )

    parser.add_argument('--three-way', action='store_true',
                       help='Analyze 3-way interaction')
    parser.add_argument('--four-way', action='store_true',
                       help='Analyze 4-way interaction')
    parser.add_argument('--pairwise-results', type=Path, required=True,
                       help='Path to Paper 3 pairwise results JSON')
    parser.add_argument('--three-way-results', type=Path, default=None,
                       help='Path to 3-way results JSON (required for 4-way)')
    parser.add_argument('--factorial-data', type=Path, required=True,
                       help='Path to factorial experiment results JSON')
    parser.add_argument('--combination', type=str, default=None,
                       help='Combination ID (e.g., H1xH2xH4 for 3-way)')
    parser.add_argument('--metric', type=str, default='mean_population',
                       help='Metric to analyze (default: mean_population)')
    parser.add_argument('--output', type=Path, default=None,
                       help='Output JSON path (default: print to stdout)')

    args = parser.parse_args()

    if not args.three_way and not args.four_way:
        print("Error: Must specify --three-way or --four-way", file=sys.stderr)
        sys.exit(1)

    # Initialize analyzer
    analyzer = HigherOrderSynergyAnalyzer(args.pairwise_results)

    # Analyze
    if args.three_way:
        if not args.combination:
            print("Error: --combination required for 3-way analysis", file=sys.stderr)
            sys.exit(1)

        result = analyzer.analyze_3way_interaction(
            args.factorial_data,
            args.combination,
            args.metric
        )

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"3-way results exported to {args.output}")
        else:
            print(json.dumps(result, indent=2))

    elif args.four_way:
        if not args.three_way_results:
            print("Error: --three-way-results required for 4-way analysis", file=sys.stderr)
            sys.exit(1)

        # Load 3-way results
        with open(args.three_way_results, 'r') as f:
            three_way_data = json.load(f)

        result = analyzer.analyze_4way_interaction(
            args.factorial_data,
            three_way_data,
            "H1xH2xH4xH5",
            args.metric
        )

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"4-way results exported to {args.output}")
        else:
            print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
