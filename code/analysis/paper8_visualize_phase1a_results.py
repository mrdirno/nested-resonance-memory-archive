#!/usr/bin/env python3
"""
Paper 8 Phase 1A: Hypothesis Testing Results Visualization

Generate publication-quality figure for Paper 8 Phase 1A hypothesis validation:
- Figure: 5-panel hypothesis testing results (H1-H5)
- Each panel: Hypothesis description, statistical test result, VALIDATED/REFUTED badge
- Publication quality: 300 DPI, proper layout, clear interpretation

Designed for immediate execution when C256 Phase 1A analysis complete.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
import sys

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch
except ImportError:
    print("Error: numpy and matplotlib required. Install with: pip install numpy matplotlib",
          file=sys.stderr)
    sys.exit(1)

# Publication-quality settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['legend.fontsize'] = 8


class Phase1AVisualizer:
    """Generate Paper 8 Phase 1A hypothesis testing results figure."""

    def __init__(self, results: dict):
        """
        Initialize visualizer with Phase 1A results.

        Args:
            results: Phase 1A hypothesis testing results JSON
        """
        self.results = results

        # Hypothesis descriptions
        self.hypothesis_names = {
            'H1': 'System Resource Contention',
            'H2': 'Memory Fragmentation',
            'H3': 'I/O Operation Accumulation',
            'H4': 'Thermal/Frequency Throttling',
            'H5': 'Emergent Complexity'
        }

    @classmethod
    def from_json(cls, json_path: Path):
        """Load Phase 1A results from JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)
        return cls(data)

    def generate_hypothesis_results_figure(self, output_path: Path):
        """
        Generate 5-panel hypothesis testing results figure.

        Layout: 5 vertical panels (one per hypothesis)
        Each panel: Hypothesis name, test description, result, VALIDATED/REFUTED badge
        """
        fig = plt.figure(figsize=(10, 12))

        hypotheses = ['H1', 'H2', 'H3', 'H4', 'H5']
        n_hyp = len(hypotheses)

        for i, hyp_id in enumerate(hypotheses):
            ax = plt.subplot(n_hyp, 1, i + 1)

            # Get hypothesis result
            hyp_result = self.results.get(hyp_id, {})
            if not hyp_result or 'error' in hyp_result:
                self._plot_error_panel(ax, hyp_id)
                continue

            # Plot hypothesis panel
            self._plot_hypothesis_panel(ax, hyp_id, hyp_result)

        # Overall title
        fig.suptitle('Paper 8 Phase 1A: Hypothesis Testing Results (C256)',
                    fontsize=14, fontweight='bold', y=0.995)

        plt.tight_layout(rect=[0, 0, 1, 0.99])
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure saved: {output_path}")

    def _plot_hypothesis_panel(self, ax, hyp_id: str, result: dict):
        """Plot single hypothesis result panel."""
        # Clear axes
        ax.axis('off')

        # Validation status
        validated = result.get('validated', False)
        badge_color = '#2ecc71' if validated else '#e74c3c'
        badge_text = 'VALIDATED' if validated else 'REFUTED'

        # Panel background
        panel_box = FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                                  boxstyle="round,pad=0.01",
                                  facecolor='#f8f9fa',
                                  edgecolor='#dee2e6',
                                  linewidth=2,
                                  transform=ax.transAxes)
        ax.add_patch(panel_box)

        # Hypothesis ID and name
        ax.text(0.05, 0.85, f"{hyp_id}: {self.hypothesis_names[hyp_id]}",
               transform=ax.transAxes,
               fontsize=12, fontweight='bold',
               verticalalignment='top')

        # Validation badge
        badge_box = FancyBboxPatch((0.75, 0.75), 0.2, 0.15,
                                  boxstyle="round,pad=0.01",
                                  facecolor=badge_color,
                                  edgecolor='black',
                                  linewidth=1.5,
                                  transform=ax.transAxes)
        ax.add_patch(badge_box)

        ax.text(0.85, 0.825, badge_text,
               transform=ax.transAxes,
               fontsize=10, fontweight='bold',
               color='white',
               horizontalalignment='center',
               verticalalignment='center')

        # Test description
        test_desc = self._get_test_description(hyp_id)
        ax.text(0.05, 0.70, f"Test: {test_desc}",
               transform=ax.transAxes,
               fontsize=9,
               verticalalignment='top',
               style='italic')

        # Statistical results
        stat_text = self._format_statistical_results(hyp_id, result)
        ax.text(0.05, 0.55, stat_text,
               transform=ax.transAxes,
               fontsize=9,
               verticalalignment='top',
               family='monospace')

        # Interpretation
        interpretation = result.get('interpretation', 'No interpretation available')
        ax.text(0.05, 0.25, f"Interpretation:\n{interpretation}",
               transform=ax.transAxes,
               fontsize=9,
               verticalalignment='top',
               wrap=True)

    def _plot_error_panel(self, ax, hyp_id: str):
        """Plot error panel for missing/invalid hypothesis."""
        ax.axis('off')

        # Error background
        error_box = FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                                  boxstyle="round,pad=0.01",
                                  facecolor='#f8d7da',
                                  edgecolor='#f5c6cb',
                                  linewidth=2,
                                  transform=ax.transAxes)
        ax.add_patch(error_box)

        ax.text(0.05, 0.85, f"{hyp_id}: {self.hypothesis_names.get(hyp_id, 'Unknown')}",
               transform=ax.transAxes,
               fontsize=12, fontweight='bold',
               verticalalignment='top')

        ax.text(0.5, 0.5, 'ERROR: Test results not available',
               transform=ax.transAxes,
               fontsize=10, color='#721c24',
               horizontalalignment='center',
               verticalalignment='center')

    def _get_test_description(self, hyp_id: str) -> str:
        """Get statistical test description for hypothesis."""
        test_descriptions = {
            'H1': 'Spearman rank correlation (runtime vs CPU availability)',
            'H2': 'Polynomial (degree 2) vs. linear regression (memory growth)',
            'H3': 'Linear regression (runtime vs cycle number)',
            'H4': 'Spearman rank correlation (runtime vs thermal metrics)',
            'H5': 'Linear regression (runtime vs pattern memory size)'
        }
        return test_descriptions.get(hyp_id, 'Unknown test')

    def _format_statistical_results(self, hyp_id: str, result: dict) -> str:
        """Format statistical results for display."""
        if hyp_id in ['H1', 'H4']:  # Spearman correlation
            rho = result.get('rho', 0.0)
            p_value = result.get('p_value', 1.0)
            threshold = result.get('threshold', 0.3)
            return f"ρ = {rho:.4f}, p = {p_value:.4f}\nThreshold: |ρ| > {threshold}, p < 0.05\nResult: {'✓ Significant' if result.get('validated') else '✗ Not significant'}"

        elif hyp_id == 'H2':  # Polynomial regression
            r2_linear = result.get('r2_linear', 0.0)
            r2_poly = result.get('r2_poly', 0.0)
            delta_r2 = result.get('delta_r2', 0.0)
            return f"R² (linear) = {r2_linear:.4f}\nR² (poly) = {r2_poly:.4f}\nΔR² = {delta_r2:.4f}\nThreshold: ΔR² > 0.1\nResult: {'✓ Non-linear growth detected' if result.get('validated') else '✗ Linear growth only'}"

        elif hyp_id in ['H3', 'H5']:  # Linear regression
            slope = result.get('slope', 0.0)
            p_value = result.get('p_value', 1.0)
            r2 = result.get('r2', 0.0)
            return f"Slope (β₁) = {slope:.6f}, p = {p_value:.4f}\nR² = {r2:.4f}\nThreshold: β₁ > 0, p < 0.05, R² > 0.3\nResult: {'✓ Significant trend' if result.get('validated') else '✗ No significant trend'}"

        return "Statistical results unavailable"


def main():
    parser = argparse.ArgumentParser(
        description='Generate Paper 8 Phase 1A hypothesis testing results figure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate hypothesis testing figure
  python paper8_visualize_phase1a_results.py \\
      --results paper8_phase1a_results.json \\
      --output data/figures/paper8/paper8_fig_phase1a_hypothesis_results.png
        """
    )

    parser.add_argument('--results', type=Path, required=True,
                       help='Phase 1A hypothesis testing results JSON')
    parser.add_argument('--output', type=Path, required=True,
                       help='Output PNG file path')

    args = parser.parse_args()

    # Load results
    if not args.results.exists():
        print(f"Error: Results file not found at {args.results}", file=sys.stderr)
        sys.exit(1)

    visualizer = Phase1AVisualizer.from_json(args.results)
    visualizer.generate_hypothesis_results_figure(args.output)


if __name__ == '__main__':
    main()
