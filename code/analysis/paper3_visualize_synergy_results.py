#!/usr/bin/env python3
"""
Paper 3: Synergy Results Visualization

Generate publication-quality figures for Paper 3 factorial validation:
- Figure 1: Classification summary (bar chart: SYNERGISTIC/ANTAGONISTIC/ADDITIVE distribution)
- Figure 2: Synergy magnitude ranking (horizontal bar chart with color coding)
- Figure 3: Interaction pattern matrix (4×4 heatmap: H1, H2, H4, H5)
- Figure 4: Mechanism involvement analysis (stacked bar chart per mechanism)

Designed for immediate execution when Phase 1+2 analysis complete (zero-delay finalization).

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List
import sys

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
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


class SynergyVisualizer:
    """Generate Paper 3 figures from Phase 1+2 analysis results."""

    def __init__(self, phase1_results: Dict, phase2_comparison: Dict = None):
        """
        Initialize visualizer with analysis results.

        Args:
            phase1_results: Phase 1 classification results (per-pair)
            phase2_comparison: Phase 2 comparison results (cross-pair analysis)
        """
        self.phase1 = phase1_results
        self.phase2 = phase2_comparison

        # Color scheme
        self.colors = {
            'SYNERGISTIC': '#2ecc71',    # Green (positive interaction)
            'ANTAGONISTIC': '#e74c3c',   # Red (negative interaction)
            'ADDITIVE': '#3498db'        # Blue (no interaction)
        }

    @classmethod
    def from_json(cls, phase1_path: Path, phase2_path: Path = None):
        """Load analysis results from JSON files."""
        with open(phase1_path, 'r') as f:
            phase1_data = json.load(f)

        phase2_data = None
        if phase2_path and phase2_path.exists():
            with open(phase2_path, 'r') as f:
                phase2_data = json.load(f)

        return cls(phase1_data, phase2_data)

    def figure1_classification_summary(self, output_path: Path):
        """
        Figure 1: Classification Summary (Bar Chart)

        Vertical bar chart showing distribution of classifications:
        - SYNERGISTIC (green)
        - ANTAGONISTIC (red)
        - ADDITIVE (blue)
        """
        # Count classifications
        distribution = {'SYNERGISTIC': 0, 'ANTAGONISTIC': 0, 'ADDITIVE': 0}
        for pair_id, result in self.phase1.items():
            if 'error' not in result:
                classification = result['classification']
                distribution[classification] += 1

        # Create figure
        fig, ax = plt.subplots(figsize=(6, 4))

        classifications = list(distribution.keys())
        counts = list(distribution.values())
        colors = [self.colors[c] for c in classifications]

        bars = ax.bar(classifications, counts, color=colors, edgecolor='black', linewidth=1.5)

        # Add count labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_ylabel('Number of Pairs', fontsize=11, fontweight='bold')
        ax.set_title('Figure 1: Mechanism Interaction Classification Distribution',
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_ylim(0, max(counts) * 1.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 1 saved: {output_path}")

    def figure2_synergy_magnitude_ranking(self, output_path: Path):
        """
        Figure 2: Synergy Magnitude Ranking (Horizontal Bar Chart)

        Horizontal bars showing synergy for each pair, color-coded by classification.
        Sorted by synergy magnitude (most positive to most negative).
        """
        # Extract synergy data
        synergy_data = []
        for pair_id, result in self.phase1.items():
            if 'error' not in result:
                synergy_pct = result['synergy']['synergy_percent']
                classification = result['classification']
                synergy_data.append((pair_id, synergy_pct, classification))

        # Sort by synergy (descending: most positive first)
        synergy_data.sort(key=lambda x: x[1], reverse=True)

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 5))

        pairs = [x[0] for x in synergy_data]
        synergies = [x[1] for x in synergy_data]
        colors = [self.colors[x[2]] for x in synergy_data]

        y_pos = np.arange(len(pairs))
        bars = ax.barh(y_pos, synergies, color=colors, edgecolor='black', linewidth=1.2)

        # Add synergy values at end of bars
        for i, (bar, synergy) in enumerate(zip(bars, synergies)):
            x_pos = synergy + (2 if synergy > 0 else -2)
            ha = 'left' if synergy > 0 else 'right'
            ax.text(x_pos, bar.get_y() + bar.get_height()/2.,
                   f'{synergy:+.1f}%',
                   ha=ha, va='center', fontsize=9, fontweight='bold')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(pairs, fontsize=10, fontweight='bold')
        ax.set_xlabel('Synergy (% of Baseline)', fontsize=11, fontweight='bold')
        ax.set_title('Figure 2: Mechanism Interaction Synergy Magnitude',
                    fontsize=12, fontweight='bold', pad=15)
        ax.axvline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Legend
        legend_elements = [
            mpatches.Patch(facecolor=self.colors['SYNERGISTIC'], edgecolor='black',
                          label='Synergistic (>+10%)'),
            mpatches.Patch(facecolor=self.colors['ADDITIVE'], edgecolor='black',
                          label='Additive (±10%)'),
            mpatches.Patch(facecolor=self.colors['ANTAGONISTIC'], edgecolor='black',
                          label='Antagonistic (<-10%)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 2 saved: {output_path}")

    def figure3_interaction_matrix(self, output_path: Path):
        """
        Figure 3: Interaction Pattern Matrix (Heatmap)

        4×4 triangular matrix showing synergy for all mechanism pairs.
        Color intensity = synergy magnitude, color hue = positive/negative.
        """
        mechanisms = ['H1', 'H2', 'H4', 'H5']
        n = len(mechanisms)

        # Initialize matrix (NaN for lower triangle + diagonal)
        matrix = np.full((n, n), np.nan)

        # Fill upper triangle with synergy values
        for pair_id, result in self.phase1.items():
            if 'error' in result:
                continue

            # Parse pair ID (e.g., 'H1xH2' → indices 0, 1)
            mech_names = pair_id.replace('x', ' ').split()
            if len(mech_names) != 2:
                continue

            try:
                i = mechanisms.index(mech_names[0])
                j = mechanisms.index(mech_names[1])
                if i < j:  # Upper triangle only
                    synergy_pct = result['synergy']['synergy_percent']
                    matrix[i, j] = synergy_pct
            except ValueError:
                continue

        # Create figure
        fig, ax = plt.subplots(figsize=(7, 6))

        # Custom colormap: red (negative) → white (zero) → green (positive)
        from matplotlib.colors import LinearSegmentedColormap
        colors_map = ['#e74c3c', '#ffffff', '#2ecc71']  # Red → White → Green
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('synergy', colors_map, N=n_bins)

        # Symmetric color scale around zero
        vmax = max(abs(np.nanmin(matrix)), abs(np.nanmax(matrix)))
        vmin = -vmax

        # Plot heatmap
        im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')

        # Annotations (synergy values + classifications)
        for i in range(n):
            for j in range(n):
                if not np.isnan(matrix[i, j]):
                    synergy = matrix[i, j]
                    pair_id = f"{mechanisms[i]}x{mechanisms[j]}"
                    classification = self.phase1[pair_id]['classification']

                    # Color text for readability
                    text_color = 'white' if abs(synergy) > vmax * 0.6 else 'black'

                    # Synergy value
                    ax.text(j, i, f'{synergy:+.1f}%',
                           ha='center', va='center',
                           fontsize=10, fontweight='bold', color=text_color)

                    # Classification (abbreviated)
                    abbrev = {'SYNERGISTIC': 'SYN', 'ANTAGONISTIC': 'ANT', 'ADDITIVE': 'ADD'}
                    ax.text(j, i + 0.35, abbrev[classification],
                           ha='center', va='center',
                           fontsize=8, style='italic', color=text_color)

        # Ticks and labels
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels(mechanisms, fontsize=11, fontweight='bold')
        ax.set_yticklabels(mechanisms, fontsize=11, fontweight='bold')
        ax.set_xlabel('Mechanism B', fontsize=11, fontweight='bold')
        ax.set_ylabel('Mechanism A', fontsize=11, fontweight='bold')
        ax.set_title('Figure 3: Pairwise Mechanism Interaction Matrix',
                    fontsize=12, fontweight='bold', pad=15)

        # Colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Synergy (% of Baseline)', rotation=270, labelpad=20,
                      fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 3 saved: {output_path}")

    def figure4_mechanism_involvement(self, output_path: Path):
        """
        Figure 4: Mechanism Involvement Analysis (Stacked Bar Chart)

        Stacked horizontal bars for each mechanism showing:
        - Green segment: # pairs synergistic
        - Blue segment: # pairs additive
        - Red segment: # pairs antagonistic
        """
        if not self.phase2 or 'mechanism_involvement' not in self.phase2:
            print("Warning: Phase 2 results required for Figure 4. Skipping.")
            return

        involvement = self.phase2['mechanism_involvement']
        mechanisms = ['H1', 'H2', 'H4', 'H5']

        # Extract counts
        synergistic_counts = [len(involvement[m]['synergistic']) for m in mechanisms]
        additive_counts = [len(involvement[m]['additive']) for m in mechanisms]
        antagonistic_counts = [len(involvement[m]['antagonistic']) for m in mechanisms]

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 5))

        y_pos = np.arange(len(mechanisms))
        bar_height = 0.6

        # Stacked bars
        bars1 = ax.barh(y_pos, synergistic_counts, bar_height,
                       label='Synergistic', color=self.colors['SYNERGISTIC'],
                       edgecolor='black', linewidth=1.2)

        bars2 = ax.barh(y_pos, additive_counts, bar_height,
                       left=synergistic_counts,
                       label='Additive', color=self.colors['ADDITIVE'],
                       edgecolor='black', linewidth=1.2)

        bars3 = ax.barh(y_pos, antagonistic_counts, bar_height,
                       left=np.array(synergistic_counts) + np.array(additive_counts),
                       label='Antagonistic', color=self.colors['ANTAGONISTIC'],
                       edgecolor='black', linewidth=1.2)

        # Labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(mechanisms, fontsize=11, fontweight='bold')
        ax.set_xlabel('Number of Pairs Involved', fontsize=11, fontweight='bold')
        ax.set_title('Figure 4: Mechanism Involvement in Interaction Types',
                    fontsize=12, fontweight='bold', pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(loc='lower right', framealpha=0.9)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Figure 4 saved: {output_path}")

    def generate_all_figures(self, output_dir: Path):
        """Generate all Paper 3 figures."""
        output_dir.mkdir(parents=True, exist_ok=True)

        self.figure1_classification_summary(output_dir / 'paper3_fig1_classification_summary.png')
        self.figure2_synergy_magnitude_ranking(output_dir / 'paper3_fig2_synergy_ranking.png')
        self.figure3_interaction_matrix(output_dir / 'paper3_fig3_interaction_matrix.png')

        if self.phase2:
            self.figure4_mechanism_involvement(output_dir / 'paper3_fig4_mechanism_involvement.png')

        print(f"\nAll figures saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Paper 3 figures from synergy analysis results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all figures
  python paper3_visualize_synergy_results.py \\
      --phase1 paper3_phase1_results.json \\
      --phase2 paper3_phase2_comparison.json \\
      --output data/figures/paper3/

  # Generate only Phase 1 figures (Figures 1-3)
  python paper3_visualize_synergy_results.py \\
      --phase1 paper3_phase1_results.json \\
      --output data/figures/paper3/

  # Generate specific figure
  python paper3_visualize_synergy_results.py \\
      --phase1 paper3_phase1_results.json \\
      --figure 1 \\
      --output paper3_fig1.png
        """
    )

    parser.add_argument('--phase1', type=Path, required=True,
                       help='Phase 1 classification results JSON')
    parser.add_argument('--phase2', type=Path, default=None,
                       help='Phase 2 comparison results JSON (optional, required for Figure 4)')
    parser.add_argument('--output', type=Path, required=True,
                       help='Output path (directory for all figures, or single file path)')
    parser.add_argument('--figure', type=int, choices=[1, 2, 3, 4], default=None,
                       help='Generate specific figure only (default: all)')

    args = parser.parse_args()

    # Load results
    if not args.phase1.exists():
        print(f"Error: Phase 1 results not found at {args.phase1}", file=sys.stderr)
        sys.exit(1)

    visualizer = SynergyVisualizer.from_json(args.phase1, args.phase2)

    # Generate figures
    if args.figure:
        # Single figure
        if args.output.suffix != '.png':
            print("Error: Output must be PNG file path for single figure", file=sys.stderr)
            sys.exit(1)

        if args.figure == 1:
            visualizer.figure1_classification_summary(args.output)
        elif args.figure == 2:
            visualizer.figure2_synergy_magnitude_ranking(args.output)
        elif args.figure == 3:
            visualizer.figure3_interaction_matrix(args.output)
        elif args.figure == 4:
            if not args.phase2:
                print("Error: Phase 2 results required for Figure 4", file=sys.stderr)
                sys.exit(1)
            visualizer.figure4_mechanism_involvement(args.output)
    else:
        # All figures (output must be directory)
        visualizer.generate_all_figures(args.output)


if __name__ == '__main__':
    main()
