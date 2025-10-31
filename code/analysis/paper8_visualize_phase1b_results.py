#!/usr/bin/env python3
"""
Paper 8 Phase 1B: Optimization Comparison Results Visualization

Generate publication-quality figures for Paper 8 Phase 1B validation:
- Figure 1: Runtime speedup comparison (bar chart with error bars)
- Figure 2: Variance comparison (before/after with % reduction annotation)
- Figure 3: Statistical significance panel (t-test, Levene's test, Cohen's d)

Designed for immediate execution when C256 + C257-C260 Phase 1B analysis complete.

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
    from matplotlib.patches import FancyBboxPatch
except ImportError:
    print("Error: numpy and matplotlib required. Install with: pip install numpy matplotlib",
          file=sys.stderr)
    sys.exit(1)

# Publication-quality settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['legend.fontsize'] = 9


class Phase1BVisualizer:
    """Generate Paper 8 Phase 1B optimization comparison figures."""

    def __init__(self, results: dict):
        """
        Initialize visualizer with Phase 1B results.

        Args:
            results: Phase 1B optimization comparison results JSON
        """
        self.results = results

    @classmethod
    def from_json(cls, json_path: Path):
        """Load Phase 1B results from JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)
        return cls(data)

    def generate_all_figures(self, output_dir: Path):
        """Generate all Phase 1B figures."""
        output_dir.mkdir(parents=True, exist_ok=True)

        self.figure1_runtime_speedup(output_dir / 'paper8_fig_phase1b_speedup.png')
        self.figure2_variance_comparison(output_dir / 'paper8_fig_phase1b_variance.png')
        self.figure3_statistical_significance(output_dir / 'paper8_fig_phase1b_statistics.png')

        print(f"\nAll Phase 1B figures saved to {output_dir}")

    def figure1_runtime_speedup(self, output_path: Path):
        """
        Figure 1: Runtime Speedup Comparison

        Bar chart showing:
        - C256 (baseline) runtime
        - C257-C260 (optimized) runtimes
        - Speedup factors annotated
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract runtime data
        runtime_comp = self.results.get('runtime_comparison', {})

        experiments = ['C256\n(Baseline)', 'C257\n(Opt)', 'C258\n(Opt)', 'C259\n(Opt)', 'C260\n(Opt)']
        runtimes_hours = []
        speedups = []

        # C256 baseline
        c256_runtime = runtime_comp.get('baseline_runtime_hours', 0)
        runtimes_hours.append(c256_runtime)
        speedups.append('1.0×')

        # Optimized experiments
        for exp_id in ['C257', 'C258', 'C259', 'C260']:
            opt_data = runtime_comp.get('optimized', {}).get(exp_id, {})
            runtime = opt_data.get('runtime_hours', 0)
            speedup = opt_data.get('speedup', 1.0)
            runtimes_hours.append(runtime)
            speedups.append(f"{speedup:.1f}×")

        # Bar chart
        colors = ['#3498db'] + ['#2ecc71'] * 4
        bars = ax.bar(experiments, runtimes_hours, color=colors, edgecolor='black', linewidth=1.5)

        # Annotate bars with runtime and speedup
        for bar, runtime, speedup in zip(bars, runtimes_hours, speedups):
            height = bar.get_height()

            # Runtime label
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{runtime:.2f}h',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

            # Speedup label (if not baseline)
            if speedup != '1.0×':
                ax.text(bar.get_x() + bar.get_width()/2., height/2,
                       speedup,
                       ha='center', va='center', fontsize=11, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

        ax.set_ylabel('Runtime (hours)', fontsize=11, fontweight='bold')
        ax.set_title('Figure: Runtime Speedup Comparison (C256 Baseline vs. C257-C260 Optimized)',
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_ylim(0, max(runtimes_hours) * 1.15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Expected speedup annotation
        expected_speedup = runtime_comp.get('expected_speedup', '160-190×')
        ax.text(0.02, 0.98, f'Expected speedup: {expected_speedup}\n(1.08M psutil calls → 12K calls)',
               transform=ax.transAxes, fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 1 saved: {output_path}")

    def figure2_variance_comparison(self, output_path: Path):
        """
        Figure 2: Variance Comparison (Critical H2+H3 Test)

        Side-by-side comparison:
        - C256 variance (before optimization)
        - C257-C260 mean variance (after optimization)
        - Variance reduction percentage annotated
        - Critical threshold line (80% reduction required for H2+H3 validation)
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Extract variance data
        variance_comp = self.results.get('variance_comparison', {})

        variance_c256 = variance_comp.get('baseline_variance', 0)
        variance_optimized = variance_comp.get('optimized_mean_variance', 0)
        reduction_pct = variance_comp.get('variance_reduction_pct', 0)
        h2_h3_validated = variance_comp.get('h2_h3_validated', False)

        variances = [variance_c256, variance_optimized]
        labels = ['C256\n(Unoptimized)', 'C257-C260\n(Optimized\nMean)']
        colors = ['#e74c3c', '#2ecc71' if h2_h3_validated else '#f39c12']

        bars = ax.bar(labels, variances, color=colors, edgecolor='black', linewidth=1.5)

        # Annotate bars
        for bar, variance in zip(bars, variances):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{variance:.4f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Variance reduction annotation
        ax.annotate('', xy=(1, variances[1]), xytext=(0, variances[0]),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2))

        mid_x = 0.5
        mid_y = (variances[0] + variances[1]) / 2
        reduction_text = f'{reduction_pct:.1f}% reduction'
        ax.text(mid_x, mid_y, reduction_text,
               ha='center', va='center', fontsize=11, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='black', lw=2))

        ax.set_ylabel('Variance (runtime²)', fontsize=11, fontweight='bold')
        ax.set_title('Figure: Variance Comparison (Critical H2+H3 Falsifiable Prediction Test)',
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_ylim(0, max(variances) * 1.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # H2+H3 validation result
        validation_text = 'H2+H3 VALIDATED' if h2_h3_validated else 'H2+H3 REFUTED'
        validation_color = '#2ecc71' if h2_h3_validated else '#e74c3c'

        ax.text(0.98, 0.98, f'{validation_text}\n(Threshold: >80% reduction)',
               transform=ax.transAxes, fontsize=10, fontweight='bold',
               ha='right', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=validation_color,
                        edgecolor='black', lw=2, alpha=0.8),
               color='white')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 2 saved: {output_path}")

    def figure3_statistical_significance(self, output_path: Path):
        """
        Figure 3: Statistical Significance Panel

        3-panel layout:
        - Panel 1: t-test (runtime difference)
        - Panel 2: Levene's test (variance equality)
        - Panel 3: Cohen's d (effect size)
        """
        fig = plt.figure(figsize=(10, 8))

        # Extract statistical test data
        stats = self.results.get('statistical_tests', {})

        # Panel 1: t-test
        ax1 = plt.subplot(3, 1, 1)
        self._plot_ttest_panel(ax1, stats.get('t_test', {}))

        # Panel 2: Levene's test
        ax2 = plt.subplot(3, 1, 2)
        self._plot_levene_panel(ax2, stats.get('levene_test', {}))

        # Panel 3: Cohen's d
        ax3 = plt.subplot(3, 1, 3)
        self._plot_cohens_d_panel(ax3, stats.get('effect_size', {}))

        fig.suptitle('Figure: Statistical Significance Tests (C256 vs. C257-C260)',
                    fontsize=13, fontweight='bold', y=0.995)

        plt.tight_layout(rect=[0, 0, 1, 0.99])
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 3 saved: {output_path}")

    def _plot_ttest_panel(self, ax, t_test_data: dict):
        """Plot t-test results panel."""
        ax.axis('off')

        # Panel background
        panel_box = FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                                  boxstyle="round,pad=0.01",
                                  facecolor='#f8f9fa',
                                  edgecolor='#dee2e6',
                                  linewidth=2,
                                  transform=ax.transAxes)
        ax.add_patch(panel_box)

        # Title
        ax.text(0.05, 0.85, 'Independent Samples t-test (Runtime Difference)',
               transform=ax.transAxes, fontsize=11, fontweight='bold')

        # Results
        t_stat = t_test_data.get('t_statistic', 0.0)
        p_value = t_test_data.get('p_value', 1.0)
        significant = t_test_data.get('significant', False)

        results_text = f"t-statistic: {t_stat:.4f}\np-value: {p_value:.6f}"
        ax.text(0.05, 0.65, results_text, transform=ax.transAxes,
               fontsize=10, family='monospace')

        # Significance badge
        badge_text = 'SIGNIFICANT' if significant else 'NOT SIGNIFICANT'
        badge_color = '#2ecc71' if significant else '#e74c3c'

        ax.text(0.75, 0.5, badge_text, transform=ax.transAxes,
               fontsize=10, fontweight='bold', ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=badge_color,
                        edgecolor='black', lw=1.5, alpha=0.8),
               color='white')

        # Interpretation
        interp = "Runtime difference is statistically significant (p < 0.001)" if significant else \
                 "Runtime difference not statistically significant"
        ax.text(0.05, 0.25, f"Interpretation:\n{interp}",
               transform=ax.transAxes, fontsize=9, style='italic')

    def _plot_levene_panel(self, ax, levene_data: dict):
        """Plot Levene's test results panel."""
        ax.axis('off')

        # Panel background
        panel_box = FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                                  boxstyle="round,pad=0.01",
                                  facecolor='#f8f9fa',
                                  edgecolor='#dee2e6',
                                  linewidth=2,
                                  transform=ax.transAxes)
        ax.add_patch(panel_box)

        # Title
        ax.text(0.05, 0.85, "Levene's Test (Variance Equality)",
               transform=ax.transAxes, fontsize=11, fontweight='bold')

        # Results
        w_stat = levene_data.get('statistic', 0.0)
        p_value = levene_data.get('p_value', 1.0)
        equal_variances = levene_data.get('equal_variances', False)

        results_text = f"W-statistic: {w_stat:.4f}\np-value: {p_value:.6f}"
        ax.text(0.05, 0.65, results_text, transform=ax.transAxes,
               fontsize=10, family='monospace')

        # Variance equality badge
        badge_text = 'UNEQUAL VARIANCES' if not equal_variances else 'EQUAL VARIANCES'
        badge_color = '#2ecc71' if not equal_variances else '#e74c3c'

        ax.text(0.75, 0.5, badge_text, transform=ax.transAxes,
               fontsize=9, fontweight='bold', ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=badge_color,
                        edgecolor='black', lw=1.5, alpha=0.8),
               color='white')

        # Interpretation
        interp = "Variances significantly different (p < 0.05, optimization eliminated variance)" if not equal_variances else \
                 "Variances not significantly different (variance persists)"
        ax.text(0.05, 0.25, f"Interpretation:\n{interp}",
               transform=ax.transAxes, fontsize=9, style='italic', wrap=True)

    def _plot_cohens_d_panel(self, ax, effect_size_data: dict):
        """Plot Cohen's d effect size panel."""
        ax.axis('off')

        # Panel background
        panel_box = FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                                  boxstyle="round,pad=0.01",
                                  facecolor='#f8f9fa',
                                  edgecolor='#dee2e6',
                                  linewidth=2,
                                  transform=ax.transAxes)
        ax.add_patch(panel_box)

        # Title
        ax.text(0.05, 0.85, "Cohen's d (Effect Size)",
               transform=ax.transAxes, fontsize=11, fontweight='bold')

        # Results
        cohens_d = effect_size_data.get('cohens_d', 0.0)
        interpretation = effect_size_data.get('interpretation', 'unknown')

        results_text = f"Cohen's d: {cohens_d:.4f}"
        ax.text(0.05, 0.65, results_text, transform=ax.transAxes,
               fontsize=10, family='monospace', fontweight='bold')

        # Effect size interpretation
        effect_sizes = {
            'negligible': ('#95a5a6', 'd < 0.2'),
            'small': ('#3498db', '0.2 ≤ d < 0.5'),
            'medium': ('#f39c12', '0.5 ≤ d < 0.8'),
            'large': ('#e67e22', '0.8 ≤ d < 1.2'),
            'very large': ('#e74c3c', 'd ≥ 1.2')
        }

        badge_color = effect_sizes.get(interpretation, ('#95a5a6', ''))[0]
        badge_range = effect_sizes.get(interpretation, ('#95a5a6', ''))[1]

        ax.text(0.75, 0.55, interpretation.upper(), transform=ax.transAxes,
               fontsize=10, fontweight='bold', ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=badge_color,
                        edgecolor='black', lw=1.5, alpha=0.8),
               color='white')

        ax.text(0.75, 0.35, badge_range, transform=ax.transAxes,
               fontsize=8, ha='center', va='center', style='italic')

        # Practical significance
        if abs(cohens_d) >= 0.8:
            practical = "Effect size is practically significant (optimization has substantial impact)"
        elif abs(cohens_d) >= 0.5:
            practical = "Effect size is moderate (optimization has noticeable impact)"
        else:
            practical = "Effect size is small or negligible"

        ax.text(0.05, 0.25, f"Interpretation:\n{practical}",
               transform=ax.transAxes, fontsize=9, style='italic', wrap=True)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Paper 8 Phase 1B optimization comparison figures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all Phase 1B figures
  python paper8_visualize_phase1b_results.py \\
      --results paper8_phase1b_results.json \\
      --output data/figures/paper8/

  # Generate single figure
  python paper8_visualize_phase1b_results.py \\
      --results paper8_phase1b_results.json \\
      --output paper8_fig_speedup.png \\
      --figure 1
        """
    )

    parser.add_argument('--results', type=Path, required=True,
                       help='Phase 1B optimization comparison results JSON')
    parser.add_argument('--output', type=Path, required=True,
                       help='Output directory (for all figures) or file path (for single figure)')
    parser.add_argument('--figure', type=int, choices=[1, 2, 3], default=None,
                       help='Generate specific figure only (default: all)')

    args = parser.parse_args()

    # Load results
    if not args.results.exists():
        print(f"Error: Results file not found at {args.results}", file=sys.stderr)
        sys.exit(1)

    visualizer = Phase1BVisualizer.from_json(args.results)

    if args.figure:
        # Single figure
        if args.output.suffix != '.png':
            print("Error: Output must be PNG file path for single figure", file=sys.stderr)
            sys.exit(1)

        if args.figure == 1:
            visualizer.figure1_runtime_speedup(args.output)
        elif args.figure == 2:
            visualizer.figure2_variance_comparison(args.output)
        elif args.figure == 3:
            visualizer.figure3_statistical_significance(args.output)
    else:
        # All figures
        visualizer.generate_all_figures(args.output)


if __name__ == '__main__':
    main()
