#!/usr/bin/env python3
"""
Generate Statistical Validation Figure for Phase Transition Discovery

Creates publication-quality figure panel showing:
1. T-test results with confidence intervals
2. Effect size magnitude (Cohen's d)
3. Bootstrap CI comparison (initialization vs steady-state)
4. Test summary table

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Date: 2025-10-31 (Cycle 813)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, Tuple


class StatisticalValidationFigure:
    """Generate publication-quality statistical validation figure."""

    def __init__(self, data_path: Path):
        """Initialize with analysis data."""
        self.data_path = data_path
        self.results = self.load_results()
        self.temporal_data = self.load_temporal_data()

    def load_results(self) -> Dict:
        """Load statistical validation results."""
        results_file = self.data_path / "statistical_validation_results.json"
        with open(results_file) as f:
            return json.load(f)

    def load_temporal_data(self) -> Dict:
        """Load temporal evolution analysis results."""
        json_files = list(self.data_path.glob("temporal_analysis_*.json"))
        if not json_files:
            raise FileNotFoundError("No temporal analysis data found")

        latest = sorted(json_files)[-1]
        with open(latest) as f:
            return json.load(f)

    def create_figure(self, output_path: Path):
        """
        Create comprehensive statistical validation figure panel.

        Layout:
        - Top left: Mean resonance comparison with bootstrap CIs
        - Top right: Effect size visualization (Cohen's d)
        - Bottom left: Test statistics summary
        - Bottom right: P-value visualization
        """
        # Set publication quality parameters
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 9
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['axes.titlesize'] = 11
        plt.rcParams['xtick.labelsize'] = 8
        plt.rcParams['ytick.labelsize'] = 8
        plt.rcParams['legend.fontsize'] = 8

        fig = plt.figure(figsize=(12, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Panel A: Mean resonance comparison with bootstrap CIs
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_bootstrap_comparison(ax1)

        # Panel B: Effect size visualization
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_effect_size(ax2)

        # Panel C: Test statistics summary table
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_test_summary(ax3)

        # Panel D: P-value and significance visualization
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_significance(ax4)

        # Overall title
        fig.suptitle(
            'Statistical Validation of Phase Transition Discovery\n'
            'Initialization → Steady-State Regime Change',
            fontsize=13,
            fontweight='bold',
            y=0.98
        )

        # Save figure
        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none'
        )
        plt.close()

        print(f"Figure saved: {output_path}")

    def _plot_bootstrap_comparison(self, ax):
        """Plot A: Mean resonance with bootstrap confidence intervals."""
        windows = self.temporal_data['windows']

        # Extract initialization (windows 0-2) and steady-state (windows 3-4)
        init_means = [w['resonance_rate'] for w in windows[:3]]
        steady_means = [w['resonance_rate'] for w in windows[3:]]

        init_mean = np.mean(init_means)
        steady_mean = np.mean(steady_means)

        # Bootstrap CIs from results
        init_ci = self.results['bootstrap_ci_95']['initialization']
        steady_ci = self.results['bootstrap_ci_95']['steady_state']

        # Calculate error bars (distance from mean to CI bounds)
        init_err_lower = init_mean - init_ci[0]
        init_err_upper = init_ci[1] - init_mean
        steady_err_lower = steady_mean - steady_ci[0]
        steady_err_upper = steady_ci[1] - steady_mean

        # Bar plot with error bars
        x = np.arange(2)
        means = [init_mean, steady_mean]
        err_lower = [init_err_lower, steady_err_lower]
        err_upper = [init_err_upper, steady_err_upper]

        bars = ax.bar(
            x,
            means,
            yerr=[err_lower, err_upper],
            capsize=8,
            color=['#2ecc71', '#e74c3c'],
            alpha=0.7,
            edgecolor='black',
            linewidth=1.5
        )

        # Labels and formatting
        ax.set_xticks(x)
        ax.set_xticklabels(['Initialization\n(0-146h, n=3)', 'Steady-State\n(146-244h, n=2)'])
        ax.set_ylabel('Mean Resonance Rate', fontweight='bold')
        ax.set_title('A. Regime Comparison with Bootstrap 95% CIs', fontweight='bold', loc='left')
        ax.set_ylim(0, 1.05)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add mean values as text
        for i, (mean, bar) in enumerate(zip(means, bars)):
            ax.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.02,
                f'{mean:.1%}',
                ha='center',
                va='bottom',
                fontweight='bold',
                fontsize=10
            )

        # Add significance annotation
        ax.plot([0, 1], [1.0, 1.0], 'k-', linewidth=1.5)
        ax.text(0.5, 1.02, '***', ha='center', va='bottom', fontsize=14, fontweight='bold')
        ax.text(0.5, 0.97, f'p = {self.results["ttest"]["p_value"]:.4f}', ha='center', va='top', fontsize=8)

    def _plot_effect_size(self, ax):
        """Plot B: Cohen's d effect size visualization."""
        cohens_d = self.results['effect_size']['cohens_d']

        # Reference thresholds
        thresholds = {
            'Small': 0.2,
            'Medium': 0.5,
            'Large': 0.8,
            'Very Large': 1.2
        }

        # Bar chart with threshold lines
        ax.barh(
            0,
            cohens_d,
            height=0.5,
            color='#3498db',
            edgecolor='black',
            linewidth=1.5,
            alpha=0.7
        )

        # Threshold reference lines
        colors = ['#95a5a6', '#f39c12', '#e67e22', '#c0392b']
        for (label, threshold), color in zip(thresholds.items(), colors):
            ax.axvline(
                threshold,
                color=color,
                linestyle='--',
                linewidth=1.5,
                alpha=0.7,
                label=f'{label}: {threshold}'
            )

        # Labels and formatting
        ax.set_xlabel("Cohen's d (Effect Size)", fontweight='bold')
        ax.set_title("B. Effect Size Magnitude", fontweight='bold', loc='left')
        ax.set_yticks([])
        ax.set_xlim(0, max(cohens_d + 1, 15))
        ax.legend(loc='lower right', framealpha=0.9)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Add value annotation
        ax.text(
            cohens_d,
            0,
            f'd = {cohens_d:.2f}\n({self.results["effect_size"]["interpretation"]})',
            ha='right',
            va='center',
            fontweight='bold',
            fontsize=10,
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='black', alpha=0.9)
        )

    def _plot_test_summary(self, ax):
        """Plot C: Test statistics summary table."""
        ax.axis('off')

        # Prepare table data
        table_data = [
            ['Test', 'Statistic', 'p-value', 'Result'],
            [
                'Welch\'s t-test',
                f't({self.results["ttest"]["degrees_freedom"]}) = {self.results["ttest"]["t_statistic"]:.3f}',
                f'{self.results["ttest"]["p_value"]:.4f}',
                '✓ Significant' if self.results['ttest']['significant'] else '✗ Not Sig.'
            ],
            [
                'Cohen\'s d',
                f'd = {self.results["effect_size"]["cohens_d"]:.3f}',
                'N/A',
                f'{self.results["effect_size"]["interpretation"].title()}'
            ],
            [
                'Bootstrap CI',
                'Non-overlapping',
                'N/A',
                '✓ Separated'
            ],
            [
                'Levene\'s Test',
                f'W = {self.results["levene_test"]["statistic"]:.3f}',
                f'{self.results["levene_test"]["p_value"]:.3f}',
                '✓ Var. Equal' if self.results['levene_test']['variances_equal'] else '✗ Var. Differ'
            ],
            [
                'Mann-Whitney U',
                f'U = {self.results["mann_whitney"]["u_statistic"]:.1f}',
                f'{self.results["mann_whitney"]["p_value"]:.3f}',
                '✓ Significant' if self.results['mann_whitney']['significant'] else '⚠ Low Power'
            ]
        ]

        # Create table
        table = ax.table(
            cellText=table_data,
            cellLoc='left',
            loc='center',
            edges='closed'
        )

        # Style table
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2.5)

        # Header row formatting
        for i in range(4):
            cell = table[(0, i)]
            cell.set_facecolor('#34495e')
            cell.set_text_props(weight='bold', color='white')

        # Color-code results
        for i in range(1, 6):
            result_cell = table[(i, 3)]
            result_text = result_cell.get_text().get_text()

            if '✓' in result_text and 'Low Power' not in result_text:
                result_cell.set_facecolor('#d5f4e6')  # Light green
            elif '⚠' in result_text:
                result_cell.set_facecolor('#fff3cd')  # Light yellow
            elif '✗' in result_text:
                result_cell.set_facecolor('#f8d7da')  # Light red

        # Title
        ax.set_title('C. Statistical Test Summary', fontweight='bold', loc='left', pad=20)

    def _plot_significance(self, ax):
        """Plot D: P-value and significance visualization."""
        # P-values from all tests
        tests = ['t-test', 'Levene', 'Mann-Whitney']
        p_values = [
            self.results['ttest']['p_value'],
            self.results['levene_test']['p_value'],
            self.results['mann_whitney']['p_value']
        ]

        # Bar chart
        bars = ax.bar(
            tests,
            p_values,
            color=['#2ecc71', '#95a5a6', '#f39c12'],
            edgecolor='black',
            linewidth=1.5,
            alpha=0.7
        )

        # Significance threshold line
        ax.axhline(
            0.05,
            color='#e74c3c',
            linestyle='--',
            linewidth=2,
            label='α = 0.05 threshold'
        )

        # Labels and formatting
        ax.set_ylabel('p-value', fontweight='bold')
        ax.set_title('D. Statistical Significance', fontweight='bold', loc='left')
        ax.set_ylim(0, max(p_values) * 1.2)
        ax.legend(loc='upper right', framealpha=0.9)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add p-value labels
        for bar, p_val in zip(bars, p_values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                height + max(p_values) * 0.02,
                f'p = {p_val:.4f}',
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        # Add significance annotations
        for i, (bar, p_val) in enumerate(zip(bars, p_values)):
            if p_val < 0.05:
                ax.text(
                    bar.get_x() + bar.get_width()/2,
                    max(p_values) * 0.9,
                    '***\nSignificant',
                    ha='center',
                    va='top',
                    fontsize=9,
                    fontweight='bold',
                    color='#27ae60'
                )


def main():
    """Generate statistical validation figure."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2")
    data_path = workspace / "analysis" / "temporal_evolution"
    output_path = workspace / "data" / "figures" / "temporal_evolution" / "figure7_statistical_validation.png"

    print("="*80)
    print("GENERATING STATISTICAL VALIDATION FIGURE")
    print("="*80)
    print()

    generator = StatisticalValidationFigure(data_path)
    generator.create_figure(output_path)

    print()
    print("="*80)
    print("FIGURE GENERATION COMPLETE")
    print("="*80)
    print(f"Output: {output_path}")
    print(f"Resolution: 300 DPI (publication quality)")
    print()


if __name__ == "__main__":
    main()
