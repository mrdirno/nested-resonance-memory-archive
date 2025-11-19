#!/usr/bin/env python3
"""
Paper 3 Phase 1A: C256 H1×H4 Factorial Analysis
================================================

Analyzes Cycle 256 results (first Paper 3 mechanism validation experiment)
to classify the Energy Pooling (H1) × Spawn Throttling (H4) interaction as
SYNERGISTIC, ANTAGONISTIC, or ADDITIVE.

This script processes the C256 H1×H4 factorial results and generates:
1. Detailed synergy classification analysis
2. Population trajectory comparisons across 4 conditions
3. Publication-ready figures (300 DPI)
4. Summary statistics for Paper 3 manuscript

Purpose:
  Immediate analysis infrastructure for when C256 completes, enabling
  zero-delay finalization pattern established in Cycles 682-683.

Input:
  - code/experiments/results/cycle256_h1h4_optimized_results.json
  OR
  - data/results/cycle256_h1h4_results.json (unoptimized version)

Output:
  - Terminal report with classification results
  - data/figures/paper3/c256_population_trajectories.png (Figure 1)
  - data/figures/paper3/c256_synergy_decomposition.png (Figure 2)
  - data/results/paper3_phase1a_c256_analysis.json (structured results)

Classification Criteria:
  - SYNERGISTIC: Synergy > +10% of baseline (cooperative amplification)
  - ANTAGONISTIC: Synergy < -10% of baseline (destructive interference)
  - ADDITIVE: |Synergy| ≤ 10% of baseline (independent mechanisms)

Expected Result:
  H1×H4 = ANTAGONISTIC
  Reasoning: Pooling creates agents, throttling limits creation rate
  Predicted synergy < 0 (throttling reduces pooling benefits)

Date: 2025-10-31 (Cycle 703+)
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Optional
import sys

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
except ImportError as e:
    print(f"Error: Required package missing: {e}", file=sys.stderr)
    print("Install with: pip install numpy matplotlib", file=sys.stderr)
    sys.exit(1)


class C256Analyzer:
    """
    Analyze C256 H1×H4 factorial results for Paper 3.

    Processes single factorial experiment results, classifies interaction type,
    and generates publication figures.
    """

    def __init__(self, results_path: Path):
        """
        Initialize analyzer with C256 results.

        Args:
            results_path: Path to cycle256_h1h4_*_results.json
        """
        self.results_path = results_path
        self.data = None
        self.analysis = None
        self.load_results()

    def load_results(self):
        """Load C256 experimental results from JSON."""
        if not self.results_path.exists():
            print(f"Error: Results file not found: {self.results_path}", file=sys.stderr)
            print(f"Expected location: {self.results_path.absolute()}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(self.results_path, 'r') as f:
                self.data = json.load(f)
            print(f"Loaded C256 results: {self.data['experiment']}")
            print(f"Date: {self.data['date']}")
            print(f"Cycles: {self.data['cycles']}")
            print()
        except Exception as e:
            print(f"Error loading results: {e}", file=sys.stderr)
            sys.exit(1)

    def extract_synergy_metrics(self) -> Dict:
        """
        Extract synergy analysis metrics from C256 results.

        Returns:
            Dict with classification, synergy values, and interpretation
        """
        if 'synergy_analysis' not in self.data:
            print("Error: No synergy_analysis in results", file=sys.stderr)
            sys.exit(1)

        synergy = self.data['synergy_analysis']

        # Extract condition means
        conditions = self.data['conditions']
        off_off_mean = conditions['OFF-OFF']['mean_population']
        on_off_mean = conditions['ON-OFF']['mean_population']
        off_on_mean = conditions['OFF-ON']['mean_population']
        on_on_mean = conditions['ON-ON']['mean_population']

        # Calculate effects and synergy
        h1_effect = on_off_mean - off_off_mean  # Pooling alone
        h4_effect = off_on_mean - off_off_mean  # Throttling alone
        additive_prediction = off_off_mean + h1_effect + h4_effect
        observed_combined = on_on_mean
        synergy_absolute = observed_combined - additive_prediction
        synergy_percent = (synergy_absolute / off_off_mean * 100) if off_off_mean > 0 else 0

        # Classification
        if abs(synergy_percent) < 10:
            classification = 'ADDITIVE'
            interpretation = 'Mechanisms combine additively (within ±10%)'
        elif synergy_percent > 0:
            classification = 'SYNERGISTIC'
            interpretation = 'Mechanisms cooperate (better than additive)'
        else:
            classification = 'ANTAGONISTIC'
            interpretation = 'Mechanisms interfere (worse than additive)'

        return {
            'conditions': {
                'OFF-OFF': off_off_mean,
                'ON-OFF': on_off_mean,
                'OFF-ON': off_on_mean,
                'ON-ON': on_on_mean
            },
            'effects': {
                'h1_pooling': h1_effect,
                'h4_throttling': h4_effect
            },
            'synergy': {
                'predicted_combined': additive_prediction,
                'observed_combined': observed_combined,
                'synergy_absolute': synergy_absolute,
                'synergy_percent': synergy_percent
            },
            'classification': classification,
            'interpretation': interpretation,
            'fold_changes': {
                'h1_alone': on_off_mean / off_off_mean if off_off_mean > 0 else 0,
                'h4_alone': off_on_mean / off_off_mean if off_off_mean > 0 else 0,
                'combined': on_on_mean / off_off_mean if off_off_mean > 0 else 0,
                'predicted': additive_prediction / off_off_mean if off_off_mean > 0 else 0
            }
        }

    def print_classification_report(self, metrics: Dict):
        """Print detailed classification report to terminal."""
        print("=" * 80)
        print("PAPER 3 PHASE 1A: C256 H1×H4 FACTORIAL ANALYSIS")
        print("=" * 80)
        print()
        print("CLASSIFICATION SUMMARY")
        print("-" * 80)
        print(f"Pair: H1 (Energy Pooling) × H4 (Spawn Throttling)")
        print(f"Classification: {metrics['classification']}")
        print(f"Interpretation: {metrics['interpretation']}")
        print()
        print("CONDITION MEANS")
        print("-" * 80)
        print(f"OFF-OFF (baseline):          {metrics['conditions']['OFF-OFF']:>10.4f}")
        print(f"ON-OFF (H1 only):            {metrics['conditions']['ON-OFF']:>10.4f}  "
              f"({metrics['fold_changes']['h1_alone']:.2f}× baseline)")
        print(f"OFF-ON (H4 only):            {metrics['conditions']['OFF-ON']:>10.4f}  "
              f"({metrics['fold_changes']['h4_alone']:.2f}× baseline)")
        print(f"ON-ON (both mechanisms):     {metrics['conditions']['ON-ON']:>10.4f}  "
              f"({metrics['fold_changes']['combined']:.2f}× baseline)")
        print()
        print("MECHANISM EFFECTS")
        print("-" * 80)
        print(f"H1 (Pooling) effect:         {metrics['effects']['h1_pooling']:>+10.4f}")
        print(f"H4 (Throttling) effect:      {metrics['effects']['h4_throttling']:>+10.4f}")
        print()
        print("SYNERGY ANALYSIS")
        print("-" * 80)
        print(f"Predicted (additive):        {metrics['synergy']['predicted_combined']:>10.4f}  "
              f"({metrics['fold_changes']['predicted']:.2f}× baseline)")
        print(f"Observed (actual):           {metrics['synergy']['observed_combined']:>10.4f}  "
              f"({metrics['fold_changes']['combined']:.2f}× baseline)")
        print(f"Synergy (difference):        {metrics['synergy']['synergy_absolute']:>+10.4f}  "
              f"({metrics['synergy']['synergy_percent']:+.2f}% vs baseline)")
        print()
        print(f"Classification threshold: ±10% of baseline")
        print(f"Result: {metrics['classification']} "
              f"({metrics['synergy']['synergy_percent']:+.2f}% synergy)")
        print("=" * 80)
        print()

    def generate_population_trajectories_figure(self, metrics: Dict, output_path: Path):
        """
        Generate Figure 1: Population trajectories across 4 conditions.

        Args:
            metrics: Extracted synergy metrics
            output_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Extract population histories
        conditions = self.data['conditions']
        colors = {
            'OFF-OFF': '#888888',  # Gray
            'ON-OFF': '#1f77b4',   # Blue (H1 only)
            'OFF-ON': '#ff7f0e',   # Orange (H4 only)
            'ON-ON': '#d62728'     # Red (both)
        }

        for condition_name in ['OFF-OFF', 'ON-OFF', 'OFF-ON', 'ON-ON']:
            history = conditions[condition_name]['population_history']
            cycles = range(len(history))

            # Mechanism labels
            if condition_name == 'OFF-OFF':
                label = f'{condition_name} (Baseline)'
            elif condition_name == 'ON-OFF':
                label = f'{condition_name} (H1 Pooling)'
            elif condition_name == 'OFF-ON':
                label = f'{condition_name} (H4 Throttling)'
            else:  # ON-ON
                label = f'{condition_name} (H1+H4 Combined)'

            ax.plot(cycles, history, label=label, color=colors[condition_name],
                   linewidth=2, alpha=0.9)

        # Styling
        ax.set_xlabel('Cycle', fontsize=14, fontweight='bold')
        ax.set_ylabel('Population Size', fontsize=14, fontweight='bold')
        ax.set_title('C256: H1×H4 Population Trajectories Across Factorial Conditions',
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=12, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')

        # Add classification annotation
        classification_text = (
            f"Classification: {metrics['classification']}\n"
            f"Synergy: {metrics['synergy']['synergy_percent']:+.1f}%"
        )
        ax.text(0.02, 0.98, classification_text, transform=ax.transAxes,
               fontsize=12, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        plt.tight_layout()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 1 saved: {output_path}")

    def generate_synergy_decomposition_figure(self, metrics: Dict, output_path: Path):
        """
        Generate Figure 2: Synergy decomposition bar chart.

        Shows baseline, individual effects, additive prediction, and observed combined.

        Args:
            metrics: Extracted synergy metrics
            output_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Prepare data for stacked bar chart
        labels = ['Baseline\n(OFF-OFF)', 'H1 Effect\n(Pooling)', 'H4 Effect\n(Throttling)',
                 'Additive\nPrediction', 'Observed\nCombined']

        baseline = metrics['conditions']['OFF-OFF']
        h1_effect = metrics['effects']['h1_pooling']
        h4_effect = metrics['effects']['h4_throttling']
        predicted = metrics['synergy']['predicted_combined']
        observed = metrics['synergy']['observed_combined']

        values = [baseline, h1_effect, h4_effect, predicted, observed]
        colors_bars = ['#888888', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        bars = ax.bar(labels, values, color=colors_bars, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Add synergy arrow if significant
        synergy = metrics['synergy']['synergy_absolute']
        if abs(synergy) > 0.01:  # Show arrow if synergy > 1%
            ax.annotate('', xy=(3.5, observed), xytext=(3.5, predicted),
                       arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
            ax.text(3.7, (predicted + observed) / 2,
                   f'Synergy:\n{synergy:+.4f}\n({metrics["synergy"]["synergy_percent"]:+.1f}%)',
                   fontsize=11, color='purple', fontweight='bold')

        # Styling
        ax.set_ylabel('Mean Population', fontsize=14, fontweight='bold')
        ax.set_title('C256: H1×H4 Synergy Decomposition',
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')

        # Classification box
        classification_text = f"Classification: {metrics['classification']}"
        ax.text(0.98, 0.98, classification_text, transform=ax.transAxes,
               fontsize=12, verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        plt.tight_layout()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 2 saved: {output_path}")

    def export_analysis_json(self, metrics: Dict, output_path: Path):
        """Export structured analysis results as JSON."""
        output = {
            'experiment': 'cycle256_h1h4_factorial',
            'analysis_date': self.data['date'],
            'pair': 'H1xH4',
            'mechanisms': {
                'H1': 'Energy Pooling',
                'H4': 'Spawn Throttling'
            },
            'metrics': metrics,
            'paper3_contribution': 'First of 6 pairwise factorial experiments (C255-C260)',
            'expected_outcome': 'ANTAGONISTIC (throttling constrains pooling benefits)',
            'source_file': str(self.results_path)
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Analysis results saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze C256 H1×H4 factorial results for Paper 3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze optimized C256 results
  python analyze_cycle256_phase1a.py \\
      --results code/experiments/results/cycle256_h1h4_optimized_results.json

  # Analyze unoptimized C256 results
  python analyze_cycle256_phase1a.py \\
      --results data/results/cycle256_h1h4_results.json

  # Custom output directory
  python analyze_cycle256_phase1a.py \\
      --results code/experiments/results/cycle256_h1h4_optimized_results.json \\
      --output-dir papers/figures/paper3/

Output:
  - Terminal classification report
  - c256_population_trajectories.png (Figure 1, 300 DPI)
  - c256_synergy_decomposition.png (Figure 2, 300 DPI)
  - paper3_phase1a_c256_analysis.json (structured results)
"""
    )

    parser.add_argument('--results', type=Path, required=True,
                       help='Path to cycle256_h1h4_*_results.json')
    parser.add_argument('--output-dir', type=Path, default=Path('data/figures/paper3'),
                       help='Output directory for figures (default: data/figures/paper3)')
    parser.add_argument('--json-output', type=Path,
                       default=Path('data/results/paper3_phase1a_c256_analysis.json'),
                       help='Output path for analysis JSON')

    args = parser.parse_args()

    # Initialize analyzer
    print("Initializing C256 H1×H4 factorial analyzer...")
    analyzer = C256Analyzer(args.results)

    # Extract synergy metrics
    print("Extracting synergy metrics...")
    metrics = analyzer.extract_synergy_metrics()

    # Print classification report
    analyzer.print_classification_report(metrics)

    # Generate figures
    print("Generating publication figures...")
    fig1_path = args.output_dir / 'c256_population_trajectories.png'
    analyzer.generate_population_trajectories_figure(metrics, fig1_path)

    fig2_path = args.output_dir / 'c256_synergy_decomposition.png'
    analyzer.generate_synergy_decomposition_figure(metrics, fig2_path)

    # Export structured results
    print("Exporting analysis results...")
    analyzer.export_analysis_json(metrics, args.json_output)

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Classification: {metrics['classification']}")
    print(f"Synergy: {metrics['synergy']['synergy_percent']:+.2f}%")
    print(f"Figures: {args.output_dir}")
    print(f"Results: {args.json_output}")
    print("=" * 80)


if __name__ == "__main__":
    main()
