#!/usr/bin/env python3
"""
Paper 4: Higher-Order Synergy Results Visualization

Generate publication-quality figures for Paper 4 factorial validation:
- Figure 1: 3-way synergy magnitudes (4 combinations, color-coded by emergence type)
- Figure 2: 4-way synergy decomposition (contribution from each order: 1st, 2nd, 3rd, 4th)
- Figure 3: Generalization performance (pairwise model prediction error for 3-way and 4-way)
- Figure 4: Interaction order comparison (synergy magnitude vs order: 2-way, 3-way, 4-way)
- Figure 5: Complete factorial map (hierarchical visualization: all orders combined)

Designed for immediate execution when Phase 1+2 analysis complete (zero-delay finalization).

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
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch
except ImportError:
    print("Error: numpy and matplotlib required. Install with: pip install numpy matplotlib",
          file=sys.stderr)
    sys.exit(1)

# Publication-quality figure settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 12


class HigherOrderVisualizer:
    """Generate Paper 4 figures from Phase 1+2 analysis results."""

    def __init__(
        self,
        phase1_3way: Dict,
        phase1_4way: Dict,
        phase2_generalization: Dict,
        pairwise_results: Dict = None
    ):
        """
        Initialize visualizer with analysis results.

        Args:
            phase1_3way: Phase 1 3-way synergy results
            phase1_4way: Phase 1 4-way synergy results
            phase2_generalization: Phase 2 generalization test results
            pairwise_results: Paper 3 pairwise results (for Figure 4)
        """
        self.phase1_3way = phase1_3way
        self.phase1_4way = phase1_4way
        self.phase2 = phase2_generalization
        self.pairwise = pairwise_results

        # Color scheme
        self.colors = {
            'EMERGENT_SYNERGISTIC': '#2ecc71',    # Green
            'EMERGENT_ANTAGONISTIC': '#e74c3c',   # Red
            'PAIRWISE_GENERALIZES': '#3498db',    # Blue
            'order_1': '#95a5a6',                 # Gray (1st order)
            'order_2': '#3498db',                 # Blue (2nd order)
            'order_3': '#9b59b6',                 # Purple (3rd order)
            'order_4': '#e67e22'                  # Orange (4th order)
        }

    @classmethod
    def from_json(
        cls,
        phase1_3way_path: Path,
        phase1_4way_path: Path,
        phase2_path: Path,
        pairwise_path: Path = None
    ):
        """Load analysis results from JSON files."""
        with open(phase1_3way_path, 'r') as f:
            phase1_3way = json.load(f)

        with open(phase1_4way_path, 'r') as f:
            phase1_4way = json.load(f)

        with open(phase2_path, 'r') as f:
            phase2 = json.load(f)

        pairwise = None
        if pairwise_path and pairwise_path.exists():
            with open(pairwise_path, 'r') as f:
                pairwise = json.load(f)

        return cls(phase1_3way, phase1_4way, phase2, pairwise)

    def figure1_3way_synergy_magnitudes(self, output_path: Path):
        """
        Figure 1: 3-Way Synergy Magnitudes

        Horizontal bar chart showing synergy for each 3-way combination,
        color-coded by classification (EMERGENT vs GENERALIZES).
        """
        # Extract 3-way synergy data
        synergy_data = []
        for combo_id, result in self.phase1_3way.items():
            if 'error' not in result:
                synergy_pct = result['prediction']['synergy_3way_percent']
                classification = result['classification']
                synergy_data.append((combo_id, synergy_pct, classification))

        # Sort by synergy (descending: most positive first)
        synergy_data.sort(key=lambda x: x[1], reverse=True)

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 5))

        combos = [x[0] for x in synergy_data]
        synergies = [x[1] for x in synergy_data]
        classifications = [x[2] for x in synergy_data]

        # Map classifications to colors
        color_map = {
            'EMERGENT SYNERGISTIC': self.colors['EMERGENT_SYNERGISTIC'],
            'EMERGENT ANTAGONISTIC': self.colors['EMERGENT_ANTAGONISTIC'],
            'PAIRWISE MODEL GENERALIZES': self.colors['PAIRWISE_GENERALIZES']
        }
        colors = [color_map.get(c, '#95a5a6') for c in classifications]

        y_pos = np.arange(len(combos))
        bars = ax.barh(y_pos, synergies, color=colors, edgecolor='black', linewidth=1.2)

        # Add synergy values at end of bars
        for i, (bar, synergy) in enumerate(zip(bars, synergies)):
            x_pos = synergy + (2 if synergy > 0 else -2)
            ha = 'left' if synergy > 0 else 'right'
            ax.text(x_pos, bar.get_y() + bar.get_height()/2.,
                   f'{synergy:+.1f}%',
                   ha=ha, va='center', fontsize=9, fontweight='bold')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(combos, fontsize=10, fontweight='bold')
        ax.set_xlabel('3-Way Synergy (% of Baseline)', fontsize=11, fontweight='bold')
        ax.set_title('Figure 1: 3-Way Interaction Synergy Magnitudes',
                    fontsize=12, fontweight='bold', pad=15)
        ax.axvline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Legend
        legend_elements = [
            mpatches.Patch(facecolor=self.colors['EMERGENT_SYNERGISTIC'], edgecolor='black',
                          label='Emergent Synergistic (>+10%)'),
            mpatches.Patch(facecolor=self.colors['PAIRWISE_GENERALIZES'], edgecolor='black',
                          label='Pairwise Model Generalizes (±10%)'),
            mpatches.Patch(facecolor=self.colors['EMERGENT_ANTAGONISTIC'], edgecolor='black',
                          label='Emergent Antagonistic (<-10%)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9, fontsize=8)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 1 saved: {output_path}")

    def figure2_4way_synergy_decomposition(self, output_path: Path):
        """
        Figure 2: 4-Way Synergy Decomposition

        Stacked bar chart showing contribution from each order:
        - 1st order (main effects)
        - 2nd order (pairwise synergies)
        - 3rd order (3-way synergies)
        - 4th order (emergent 4-way synergy)
        """
        if not self.phase1_4way or 'error' in self.phase1_4way:
            print("Warning: 4-way results not available for Figure 2", file=sys.stderr)
            return

        # Extract decomposition data
        baseline = self.phase1_4way.get('baseline', 0)
        observed = self.phase1_4way['prediction']['observed']

        # 1st order (main effects)
        first_order_effects = self.phase1_4way['first_order_effects']
        first_order_total = sum(first_order_effects.values())

        # 2nd order (pairwise synergies)
        second_order_synergies = self.phase1_4way['second_order_synergies']
        second_order_total = sum(second_order_synergies.values())

        # 3rd order (3-way synergies)
        third_order_synergies = self.phase1_4way['third_order_synergies']
        third_order_total = sum(third_order_synergies.values())

        # 4th order (emergent 4-way synergy)
        fourth_order_synergy = self.phase1_4way['prediction']['synergy_4way_absolute']

        # Create figure
        fig, ax = plt.subplots(figsize=(7, 5))

        # Stacked bar components
        orders = ['Baseline', '+ 1st Order\n(Main)', '+ 2nd Order\n(Pairwise)',
                 '+ 3rd Order\n(3-Way)', '+ 4th Order\n(4-Way)']

        baseline_val = baseline
        cumulative = [
            baseline_val,
            baseline_val + first_order_total,
            baseline_val + first_order_total + second_order_total,
            baseline_val + first_order_total + second_order_total + third_order_total,
            observed
        ]

        # Contribution amounts
        contributions = [
            baseline_val,
            first_order_total,
            second_order_total,
            third_order_total,
            fourth_order_synergy
        ]

        colors_stacked = [
            '#ecf0f1',  # Baseline (light gray)
            self.colors['order_1'],
            self.colors['order_2'],
            self.colors['order_3'],
            self.colors['order_4']
        ]

        x_pos = np.arange(len(orders))
        bars = ax.bar(x_pos, cumulative, color=colors_stacked, edgecolor='black', linewidth=1.2)

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, cumulative)):
            ax.text(bar.get_x() + bar.get_width()/2., val,
                   f'{val:.1f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Add contribution annotations
        for i in range(1, len(orders)):
            contribution = contributions[i]
            if abs(contribution) > 0.1:  # Only annotate non-trivial contributions
                y_mid = cumulative[i-1] + contribution / 2
                ax.text(x_pos[i], y_mid,
                       f'{contribution:+.1f}',
                       ha='center', va='center', fontsize=8, fontweight='bold',
                       color='white' if abs(contribution) > baseline * 0.1 else 'black')

        ax.set_xticks(x_pos)
        ax.set_xticklabels(orders, fontsize=9)
        ax.set_ylabel('Population (Cumulative)', fontsize=11, fontweight='bold')
        ax.set_title('Figure 2: 4-Way Interaction Decomposition by Order',
                    fontsize=12, fontweight='bold', pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Legend
        legend_elements = [
            mpatches.Patch(facecolor=colors_stacked[1], edgecolor='black', label='1st Order (Main Effects)'),
            mpatches.Patch(facecolor=colors_stacked[2], edgecolor='black', label='2nd Order (Pairwise)'),
            mpatches.Patch(facecolor=colors_stacked[3], edgecolor='black', label='3rd Order (3-Way)'),
            mpatches.Patch(facecolor=colors_stacked[4], edgecolor='black', label='4th Order (4-Way Synergy)')
        ]
        ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, fontsize=8)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 2 saved: {output_path}")

    def figure3_generalization_performance(self, output_path: Path):
        """
        Figure 3: Generalization Performance

        Dual-panel plot showing prediction errors:
        - Left: 3-way generalization (pairwise model errors)
        - Right: 4-way generalization (lower-order model error)
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        # Panel 1: 3-way generalization
        three_way_tests = self.phase2.get('three_way_tests', {})
        combo_ids = []
        mapes = []
        generalizes_flags = []

        for combo_id, result in three_way_tests.items():
            if 'error' not in result:
                combo_ids.append(combo_id)
                mapes.append(result['mape'])
                generalizes_flags.append(result['generalizes'])

        colors_3way = [self.colors['PAIRWISE_GENERALIZES'] if g else self.colors['EMERGENT_ANTAGONISTIC']
                      for g in generalizes_flags]

        y_pos = np.arange(len(combo_ids))
        bars1 = ax1.barh(y_pos, mapes, color=colors_3way, edgecolor='black', linewidth=1.2)

        # Add MAPE values
        for i, (bar, mape) in enumerate(zip(bars1, mapes)):
            ax1.text(mape + 0.5, bar.get_y() + bar.get_height()/2.,
                    f'{mape:.1f}%',
                    ha='left', va='center', fontsize=9, fontweight='bold')

        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(combo_ids, fontsize=9, fontweight='bold')
        ax1.set_xlabel('Prediction Error (MAPE %)', fontsize=10, fontweight='bold')
        ax1.set_title('3-Way Generalization\n(Pairwise Model)', fontsize=11, fontweight='bold')
        ax1.axvline(10, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='±10% Threshold')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax1.legend(loc='lower right', fontsize=8)

        # Panel 2: 4-way generalization
        four_way_test = self.phase2.get('four_way_test', {})
        if 'error' not in four_way_test:
            mape_4way = four_way_test['mape']
            generalizes_4way = four_way_test['generalizes']

            color_4way = self.colors['PAIRWISE_GENERALIZES'] if generalizes_4way else self.colors['EMERGENT_ANTAGONISTIC']

            bar2 = ax2.barh([0], [mape_4way], color=color_4way, edgecolor='black', linewidth=1.5, height=0.5)

            ax2.text(mape_4way + 0.5, 0,
                    f'{mape_4way:.1f}%',
                    ha='left', va='center', fontsize=11, fontweight='bold')

            ax2.set_yticks([0])
            ax2.set_yticklabels(['H1×H2×H4×H5'], fontsize=10, fontweight='bold')
            ax2.set_xlabel('Prediction Error (MAPE %)', fontsize=10, fontweight='bold')
            ax2.set_title('4-Way Generalization\n(Pairwise + 3-Way Model)', fontsize=11, fontweight='bold')
            ax2.axvline(10, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='±10% Threshold')
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.grid(axis='x', alpha=0.3, linestyle='--')
            ax2.set_ylim(-0.8, 0.8)
            ax2.legend(loc='lower right', fontsize=8)

        fig.suptitle('Figure 3: Generalization Performance (Prediction Errors)',
                    fontsize=12, fontweight='bold', y=1.02)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 3 saved: {output_path}")

    def figure4_interaction_order_comparison(self, output_path: Path):
        """
        Figure 4: Interaction Order Comparison

        Line plot showing synergy magnitude vs interaction order:
        - 2-way (from Paper 3 pairwise)
        - 3-way (from Paper 4 Phase 1)
        - 4-way (from Paper 4 Phase 1)

        Tests if synergy scales linearly with order or shows qualitative shifts.
        """
        if not self.pairwise:
            print("Warning: Pairwise results required for Figure 4", file=sys.stderr)
            return

        # Extract pairwise synergies (2-way)
        synergies_2way = []
        for pair_id, result in self.pairwise.items():
            if 'error' not in result:
                synergies_2way.append(abs(result['synergy']['synergy_percent']))

        # Extract 3-way synergies
        synergies_3way = []
        for combo_id, result in self.phase1_3way.items():
            if 'error' not in result:
                synergies_3way.append(abs(result['prediction']['synergy_3way_percent']))

        # Extract 4-way synergy
        synergies_4way = []
        if self.phase1_4way and 'error' not in self.phase1_4way:
            synergies_4way.append(abs(self.phase1_4way['prediction']['synergy_4way_percent']))

        # Calculate mean and std for each order
        orders = [2, 3, 4]
        means = [
            np.mean(synergies_2way) if synergies_2way else 0,
            np.mean(synergies_3way) if synergies_3way else 0,
            np.mean(synergies_4way) if synergies_4way else 0
        ]
        stds = [
            np.std(synergies_2way) if len(synergies_2way) > 1 else 0,
            np.std(synergies_3way) if len(synergies_3way) > 1 else 0,
            0  # Only one 4-way combination
        ]

        # Create figure
        fig, ax = plt.subplots(figsize=(7, 5))

        # Plot mean synergy with error bars
        ax.errorbar(orders, means, yerr=stds, marker='o', markersize=8,
                   linewidth=2, capsize=5, capthick=2, color='#3498db',
                   ecolor='#95a5a6', label='Mean |Synergy|')

        # Add individual points (scatter)
        if synergies_2way:
            ax.scatter([2] * len(synergies_2way), synergies_2way, alpha=0.5, s=50, color='#3498db')
        if synergies_3way:
            ax.scatter([3] * len(synergies_3way), synergies_3way, alpha=0.5, s=50, color='#9b59b6')
        if synergies_4way:
            ax.scatter([4] * len(synergies_4way), synergies_4way, alpha=0.5, s=100, color='#e67e22')

        # Reference line at 10% (generalization threshold)
        ax.axhline(10, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='±10% Threshold')

        ax.set_xlabel('Interaction Order (n-way)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Synergy Magnitude (% of Baseline)', fontsize=11, fontweight='bold')
        ax.set_title('Figure 4: Synergy Magnitude vs Interaction Order',
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_xticks(orders)
        ax.set_xticklabels(['2-Way\n(Pairwise)', '3-Way', '4-Way'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(alpha=0.3, linestyle='--')
        ax.legend(loc='upper left', framealpha=0.9, fontsize=9)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 4 saved: {output_path}")

    def figure5_complete_factorial_map(self, output_path: Path):
        """
        Figure 5: Complete Factorial Map

        Hierarchical tree visualization showing:
        - Baseline (center)
        - 4 main effects (1st level)
        - 6 pairwise synergies (2nd level)
        - 4 3-way synergies (3rd level)
        - 1 4-way synergy (4th level)

        Color intensity = synergy magnitude, color hue = positive/negative.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Hierarchy levels
        levels = {
            0: {'label': 'Baseline', 'items': ['OFF-OFF-OFF-OFF'], 'y': 0},
            1: {'label': '1st Order (Main Effects)', 'items': ['H1', 'H2', 'H4', 'H5'], 'y': 1.5},
            2: {'label': '2nd Order (Pairwise)', 'items': ['H1×H2', 'H1×H4', 'H1×H5', 'H2×H4', 'H2×H5', 'H4×H5'], 'y': 3.0},
            3: {'label': '3rd Order (3-Way)', 'items': ['H1×H2×H4', 'H1×H2×H5', 'H1×H4×H5', 'H2×H4×H5'], 'y': 4.5},
            4: {'label': '4th Order (4-Way)', 'items': ['H1×H2×H4×H5'], 'y': 6.0}
        }

        # Draw levels
        for level, data in levels.items():
            y = data['y']
            items = data['items']
            n_items = len(items)

            # Calculate x positions (centered)
            if n_items == 1:
                x_positions = [5.0]
            else:
                x_positions = np.linspace(1, 9, n_items)

            for i, (item, x) in enumerate(zip(items, x_positions)):
                # Determine node color based on synergy (if available)
                if level == 0:
                    color = '#ecf0f1'  # Baseline (light gray)
                    label = 'Baseline'
                elif level == 1:
                    color = self.colors['order_1']
                    label = item
                elif level == 2:
                    # Pairwise synergy
                    pair_id = item.replace('×', 'x')
                    if self.pairwise and pair_id in self.pairwise and 'error' not in self.pairwise[pair_id]:
                        synergy_pct = self.pairwise[pair_id]['synergy']['synergy_percent']
                        if synergy_pct > 10:
                            color = self.colors['EMERGENT_SYNERGISTIC']
                        elif synergy_pct < -10:
                            color = self.colors['EMERGENT_ANTAGONISTIC']
                        else:
                            color = self.colors['PAIRWISE_GENERALIZES']
                    else:
                        color = self.colors['order_2']
                    label = item
                elif level == 3:
                    # 3-way synergy
                    combo_id = item.replace('×', 'x')
                    if combo_id in self.phase1_3way and 'error' not in self.phase1_3way[combo_id]:
                        classification = self.phase1_3way[combo_id]['classification']
                        if 'SYNERGISTIC' in classification:
                            color = self.colors['EMERGENT_SYNERGISTIC']
                        elif 'ANTAGONISTIC' in classification:
                            color = self.colors['EMERGENT_ANTAGONISTIC']
                        else:
                            color = self.colors['PAIRWISE_GENERALIZES']
                    else:
                        color = self.colors['order_3']
                    label = item
                elif level == 4:
                    # 4-way synergy
                    if self.phase1_4way and 'error' not in self.phase1_4way:
                        classification = self.phase1_4way['classification']
                        if 'SYNERGISTIC' in classification:
                            color = self.colors['EMERGENT_SYNERGISTIC']
                        elif 'ANTAGONISTIC' in classification:
                            color = self.colors['EMERGENT_ANTAGONISTIC']
                        else:
                            color = self.colors['PAIRWISE_GENERALIZES']
                    else:
                        color = self.colors['order_4']
                    label = item

                # Draw node
                circle = plt.Circle((x, y), 0.25, color=color, edgecolor='black', linewidth=1.5, zorder=10)
                ax.add_patch(circle)

                # Add label
                ax.text(x, y, label, ha='center', va='center', fontsize=7, fontweight='bold', zorder=11)

        # Add level labels
        for level, data in levels.items():
            ax.text(-0.5, data['y'], data['label'], ha='right', va='center',
                   fontsize=9, fontweight='bold', style='italic')

        ax.set_xlim(-1, 10)
        ax.set_ylim(-0.5, 6.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Figure 5: Complete Factorial Map (All Interaction Orders)',
                    fontsize=12, fontweight='bold', pad=20)

        # Legend
        legend_elements = [
            mpatches.Patch(facecolor=self.colors['EMERGENT_SYNERGISTIC'], edgecolor='black',
                          label='Emergent Synergistic (>+10%)'),
            mpatches.Patch(facecolor=self.colors['PAIRWISE_GENERALIZES'], edgecolor='black',
                          label='Additive / Generalizes (±10%)'),
            mpatches.Patch(facecolor=self.colors['EMERGENT_ANTAGONISTIC'], edgecolor='black',
                          label='Emergent Antagonistic (<-10%)')
        ]
        ax.legend(handles=legend_elements, loc='lower center', ncol=3, framealpha=0.9, fontsize=8,
                 bbox_to_anchor=(0.5, -0.05))

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 5 saved: {output_path}")

    def generate_all_figures(self, output_dir: Path):
        """Generate all 5 publication figures."""
        output_dir.mkdir(parents=True, exist_ok=True)

        print("\nGenerating Paper 4 publication figures...")
        print("=" * 60)

        self.figure1_3way_synergy_magnitudes(output_dir / 'figure1_3way_synergy_magnitude.png')
        self.figure2_4way_synergy_decomposition(output_dir / 'figure2_4way_synergy_decomposition.png')
        self.figure3_generalization_performance(output_dir / 'figure3_generalization_performance.png')
        self.figure4_interaction_order_comparison(output_dir / 'figure4_interaction_order_comparison.png')
        self.figure5_complete_factorial_map(output_dir / 'figure5_complete_factorial_map.png')

        print("=" * 60)
        print(f"All figures saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Paper 4 publication figures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all figures
  python paper4_visualize_higher_order_results.py \\
      --phase1-3way paper4_phase1_3way_combined.json \\
      --phase1-4way paper4_phase1_4way.json \\
      --phase2 paper4_phase2_generalization.json \\
      --pairwise paper3_phase1_results.json \\
      --output data/figures/paper4/

  # Generate specific figure
  python paper4_visualize_higher_order_results.py \\
      --phase1-3way paper4_phase1_3way_combined.json \\
      --phase1-4way paper4_phase1_4way.json \\
      --phase2 paper4_phase2_generalization.json \\
      --figure 1 \\
      --output data/figures/paper4/
        """
    )

    parser.add_argument('--phase1-3way', type=Path, required=True,
                       help='Path to Paper 4 Phase 1 3-way results JSON')
    parser.add_argument('--phase1-4way', type=Path, required=True,
                       help='Path to Paper 4 Phase 1 4-way results JSON')
    parser.add_argument('--phase2', type=Path, required=True,
                       help='Path to Paper 4 Phase 2 generalization test JSON')
    parser.add_argument('--pairwise', type=Path, default=None,
                       help='Path to Paper 3 pairwise results JSON (for Figure 4)')
    parser.add_argument('--output', type=Path, required=True,
                       help='Output directory for figures')
    parser.add_argument('--figure', type=int, default=None,
                       help='Generate specific figure only (1-5)')

    args = parser.parse_args()

    # Load results
    visualizer = HigherOrderVisualizer.from_json(
        args.phase1_3way,
        args.phase1_4way,
        args.phase2,
        args.pairwise
    )

    # Generate figures
    if args.figure:
        if args.figure == 1:
            visualizer.figure1_3way_synergy_magnitudes(args.output / 'figure1_3way_synergy_magnitude.png')
        elif args.figure == 2:
            visualizer.figure2_4way_synergy_decomposition(args.output / 'figure2_4way_synergy_decomposition.png')
        elif args.figure == 3:
            visualizer.figure3_generalization_performance(args.output / 'figure3_generalization_performance.png')
        elif args.figure == 4:
            visualizer.figure4_interaction_order_comparison(args.output / 'figure4_interaction_order_comparison.png')
        elif args.figure == 5:
            visualizer.figure5_complete_factorial_map(args.output / 'figure5_complete_factorial_map.png')
        else:
            print(f"Error: Invalid figure number {args.figure}. Must be 1-5.", file=sys.stderr)
            sys.exit(1)
    else:
        visualizer.generate_all_figures(args.output)


if __name__ == '__main__':
    main()
