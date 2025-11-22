#!/usr/bin/env python3
"""
Visualization Tool: Higher-Order Factorial Interactions

Purpose: Generate publication-quality figures for 3-way and 4-way factorial experiments.

Usage: python visualize_higher_order_interactions.py <aggregated_results.json>

Outputs:
- Figure 1: Hierarchical interaction decomposition (bar chart)
- Figure 2: Variance explained by interaction order (pie chart)
- Figure 3: 3-way interaction 3D surface plot
- Figure 4: 4-way interaction network diagram

All figures at 300 DPI, suitable for publication.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-27 (Cycle 352)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import sys
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Tuple
from mpl_toolkits.mplot3d import Axes3D


def load_aggregated_results(filepath: Path) -> Dict:
    """Load aggregated results JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_hierarchical_decomposition_plot(aggregated: Dict, output_dir: Path):
    """
    Generate hierarchical interaction decomposition bar chart.

    Shows contribution of main effects, pairwise, 3-way, 4-way to total variance.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # C262: 3-way
    if 'cycle262' in aggregated['experiments']:
        ax = axes[0]
        exp = aggregated['experiments']['cycle262']

        # Extract values
        main_effects = list(exp['main_effects'].values())
        pairwise = list(exp['pairwise_interactions'].values())
        threeway = [exp['threeway_analysis']['super_synergy']]

        # Bar positions
        n_main = len(main_effects)
        n_pair = len(pairwise)

        x_main = np.arange(n_main)
        x_pair = np.arange(n_pair) + n_main + 0.5
        x_3way = [n_main + n_pair + 1]

        # Plot bars
        ax.bar(x_main, main_effects, color='#3182bd', label='Main Effects')
        ax.bar(x_pair, pairwise, color='#9ecae1', label='Pairwise')
        ax.bar(x_3way, threeway, color='#e6550d', label='3-Way Super-Synergy')

        # Labels
        labels = [f"M{i+1}" for i in range(n_main)] + \
                 [f"P{i+1}" for i in range(n_pair)] + \
                 ['3-Way']
        ax.set_xticks(list(x_main) + list(x_pair) + x_3way)
        ax.set_xticklabels(labels, rotation=45, ha='right')

        ax.set_ylabel('Effect Size (Population Δ)')
        ax.set_title('C262: 3-Way Factorial (H1 × H2 × H5)', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left')
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.grid(axis='y', alpha=0.3)

    # C263: 4-way
    if 'cycle263' in aggregated['experiments']:
        ax = axes[1]
        exp = aggregated['experiments']['cycle263']

        # Extract values
        main_effects = list(exp['main_effects'].values())
        pairwise = list(exp['pairwise_interactions'].values())
        threeway_terms = list(exp['fourway_analysis']['threeway_terms'].values())
        fourway = [exp['fourway_analysis']['super_synergy']]

        # Bar positions
        n_main = len(main_effects)
        n_pair = len(pairwise)
        n_3way = len(threeway_terms)

        x_main = np.arange(n_main)
        x_pair = np.arange(n_pair) + n_main + 0.5
        x_3way = np.arange(n_3way) + n_main + n_pair + 1
        x_4way = [n_main + n_pair + n_3way + 1.5]

        # Plot bars
        ax.bar(x_main, main_effects, color='#3182bd', label='Main Effects')
        ax.bar(x_pair, pairwise, color='#9ecae1', label='Pairwise')
        ax.bar(x_3way, threeway_terms, color='#fdae6b', label='3-Way')
        ax.bar(x_4way, fourway, color='#e6550d', label='4-Way Super-Synergy')

        # Labels (simplified for readability)
        labels = [f"M{i+1}" for i in range(n_main)] + \
                 [f"P{i+1}" for i in range(n_pair)] + \
                 [f"T{i+1}" for i in range(n_3way)] + \
                 ['4-Way']
        all_x = list(x_main) + list(x_pair) + list(x_3way) + x_4way
        ax.set_xticks(all_x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)

        ax.set_ylabel('Effect Size (Population Δ)')
        ax.set_title('C263: 4-Way Factorial (H1 × H2 × H4 × H5)', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    output_path = output_dir / "figure1_hierarchical_decomposition.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_variance_explained_plot(aggregated: Dict, output_dir: Path):
    """
    Generate variance explained pie/bar chart.

    Shows R² contribution of main effects, pairwise, and higher-order terms.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # C262: 3-way variance
    if 'cycle262' in aggregated['experiments']:
        ax = axes[0]
        exp = aggregated['experiments']['cycle262']
        var_exp = exp['variance_explained']

        # Calculate incremental R²
        r2_main = var_exp['r2_main']
        r2_pairwise_incr = var_exp['r2_pairwise'] - var_exp['r2_main']
        r2_residual = var_exp['r2_residual']

        # Pie chart
        sizes = [r2_main, r2_pairwise_incr, r2_residual]
        labels = [
            f"Main Effects\n({r2_main:.1%})",
            f"Pairwise\n({r2_pairwise_incr:.1%})",
            f"3-Way + Noise\n({r2_residual:.1%})"
        ]
        colors = ['#3182bd', '#9ecae1', '#e6550d']

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=90
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('C262: Variance Explained (3-Way)', fontsize=12, fontweight='bold')

    # C263: 4-way variance
    if 'cycle263' in aggregated['experiments']:
        ax = axes[1]
        exp = aggregated['experiments']['cycle263']
        var_exp = exp['variance_explained']

        # Stacked bar chart (more appropriate for 4-way with many terms)
        r2_main = var_exp['r2_main']
        r2_pairwise_incr = var_exp['r2_pairwise'] - var_exp['r2_main']
        r2_residual = var_exp['r2_residual']

        categories = ['Total Variance']
        r2_values = [
            [r2_main],
            [r2_pairwise_incr],
            [r2_residual]
        ]

        colors = ['#3182bd', '#9ecae1', '#e6550d']
        labels = ['Main Effects', 'Pairwise', '3-Way + 4-Way + Noise']

        bottom = np.zeros(1)
        for i, (r2_val, color, label) in enumerate(zip(r2_values, colors, labels)):
            ax.barh(categories, r2_val, left=bottom, color=color, label=label)
            # Add percentage text
            ax.text(
                bottom[0] + r2_val[0]/2, 0,
                f"{r2_val[0]:.1%}",
                ha='center', va='center',
                fontweight='bold', color='white'
            )
            bottom += r2_val

        ax.set_xlim(0, 1)
        ax.set_xlabel('Proportion of Variance Explained (R²)')
        ax.set_title('C263: Variance Explained (4-Way)', fontsize=12, fontweight='bold')
        ax.legend(loc='lower right')

    plt.tight_layout()

    output_path = output_dir / "figure2_variance_explained.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_3way_surface_plot(aggregated: Dict, output_dir: Path):
    """
    Generate 3D surface plot for 3-way interaction.

    Shows observed population as function of mechanism states.
    """
    if 'cycle262' not in aggregated['experiments']:
        print("⚠️  C262 not found, skipping 3-way surface plot")
        return

    exp = aggregated['experiments']['cycle262']
    conditions = exp['conditions']

    # Extract 8 conditions
    # Map binary codes to coordinates: (H1, H2, H5)
    coords_map = {
        '000': (0, 0, 0),
        '100': (1, 0, 0),
        '010': (0, 1, 0),
        '001': (0, 0, 1),
        '110': (1, 1, 0),
        '101': (1, 0, 1),
        '011': (0, 1, 1),
        '111': (1, 1, 1)
    }

    x_vals, y_vals, z_vals, pop_vals = [], [], [], []
    for code, coord in coords_map.items():
        if code in conditions:
            x_vals.append(coord[0])
            y_vals.append(coord[1])
            z_vals.append(coord[2])
            pop_vals.append(conditions[code]['mean_population'])

    # Create 3D scatter plot (surface interpolation not feasible with 8 points)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Color by population
    scatter = ax.scatter(
        x_vals, y_vals, z_vals,
        c=pop_vals, cmap='viridis', s=200,
        edgecolors='black', linewidth=1.5
    )

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.8)
    cbar.set_label('Mean Population', rotation=270, labelpad=20)

    # Labels
    ax.set_xlabel('H1 (Energy Pooling)', fontsize=11, fontweight='bold')
    ax.set_ylabel('H2 (Reality Sources)', fontsize=11, fontweight='bold')
    ax.set_zlabel('H5 (Energy Recovery)', fontsize=11, fontweight='bold')
    ax.set_title('C262: 3-Way Interaction Landscape', fontsize=12, fontweight='bold')

    # Set ticks to 0/1
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_zticks([0, 1])

    # Annotate corner (111) - full combination
    ax.text(
        1, 1, 1,
        f"  {conditions['111']['mean_population']:.2f}",
        fontsize=10, fontweight='bold', color='red'
    )

    output_path = output_dir / "figure3_3way_surface.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_interaction_network_diagram(aggregated: Dict, output_dir: Path):
    """
    Generate network diagram showing mechanism interactions.

    Nodes = mechanisms, Edges = interactions (colored by synergy type).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # C262: 3-way network
    if 'cycle262' in aggregated['experiments']:
        ax = axes[0]
        exp = aggregated['experiments']['cycle262']

        # Mechanism positions (triangle layout)
        positions = {
            'H1': (0.5, 1.0),
            'H2': (0.0, 0.0),
            'H5': (1.0, 0.0)
        }

        # Draw nodes
        for mech, (x, y) in positions.items():
            ax.scatter(x, y, s=1000, color='#3182bd', edgecolors='black', linewidth=2, zorder=3)
            ax.text(x, y, mech, ha='center', va='center', fontsize=14, fontweight='bold', color='white')

        # Draw edges (pairwise interactions)
        pairwise = exp['pairwise_interactions']
        edge_map = {
            'M1×M2': ('H1', 'H2'),
            'M1×M3': ('H1', 'H5'),
            'M2×M3': ('H2', 'H5')
        }

        for pair, (m1, m2) in edge_map.items():
            synergy = pairwise.get(pair, 0.0)
            x1, y1 = positions[m1]
            x2, y2 = positions[m2]

            # Color by synergy
            if synergy > 0.1:
                color, style = '#2ca02c', '-'  # Green, solid (synergistic)
            elif synergy < -0.1:
                color, style = '#d62728', '--'  # Red, dashed (antagonistic)
            else:
                color, style = '#7f7f7f', ':'  # Gray, dotted (additive)

            ax.plot([x1, x2], [y1, y2], color=color, linestyle=style, linewidth=3, zorder=1)

            # Add synergy value at midpoint
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y, f"{synergy:+.2f}", ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black'),
                   fontsize=9, fontweight='bold')

        # Add 3-way annotation at center
        threeway = exp['threeway_analysis']['super_synergy']
        ax.text(0.5, 0.33, f"3-Way:\n{threeway:+.2f}",
               ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#e6550d', edgecolor='black', linewidth=2),
               fontsize=11, fontweight='bold', color='white')

        ax.set_xlim(-0.2, 1.2)
        ax.set_ylim(-0.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('C262: 3-Way Interaction Network', fontsize=12, fontweight='bold')

    # C263: 4-way network (more complex, use square layout)
    if 'cycle263' in aggregated['experiments']:
        ax = axes[1]
        exp = aggregated['experiments']['cycle263']

        # Mechanism positions (square layout)
        positions = {
            'H1': (0.0, 1.0),
            'H2': (1.0, 1.0),
            'H4': (0.0, 0.0),
            'H5': (1.0, 0.0)
        }

        # Draw nodes
        for mech, (x, y) in positions.items():
            ax.scatter(x, y, s=800, color='#3182bd', edgecolors='black', linewidth=2, zorder=3)
            ax.text(x, y, mech, ha='center', va='center', fontsize=12, fontweight='bold', color='white')

        # Draw edges (pairwise interactions - only show significant ones to reduce clutter)
        pairwise = exp['pairwise_interactions']
        edge_map = {
            'M1×M2': ('H1', 'H2'),
            'M1×M3': ('H1', 'H4'),
            'M1×M4': ('H1', 'H5'),
            'M2×M3': ('H2', 'H4'),
            'M2×M4': ('H2', 'H5'),
            'M3×M4': ('H4', 'H5')
        }

        for pair, (m1, m2) in edge_map.items():
            synergy = pairwise.get(pair, 0.0)

            # Only draw significant interactions
            if abs(synergy) < 0.1:
                continue

            x1, y1 = positions[m1]
            x2, y2 = positions[m2]

            # Color by synergy
            if synergy > 0.1:
                color, style = '#2ca02c', '-'
            else:
                color, style = '#d62728', '--'

            ax.plot([x1, x2], [y1, y2], color=color, linestyle=style, linewidth=2.5, zorder=1)

        # Add 4-way annotation at center
        fourway = exp['fourway_analysis']['super_synergy']
        ax.text(0.5, 0.5, f"4-Way:\n{fourway:+.2f}",
               ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#e6550d', edgecolor='black', linewidth=2),
               fontsize=11, fontweight='bold', color='white')

        ax.set_xlim(-0.3, 1.3)
        ax.set_ylim(-0.3, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('C263: 4-Way Interaction Network', fontsize=12, fontweight='bold')

    # Legend
    legend_elements = [
        mpatches.Patch(color='#2ca02c', label='Synergistic (> +0.1)'),
        mpatches.Patch(color='#d62728', label='Antagonistic (< -0.1)'),
        mpatches.Patch(color='#7f7f7f', label='Additive (±0.1)')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=10)

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    output_path = output_dir / "figure4_interaction_network.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def main():
    """Main visualization pipeline."""
    parser = argparse.ArgumentParser(
        description='Generate visualizations for higher-order factorial experiments'
    )
    parser.add_argument(
        'results_file',
        type=Path,
        help='Path to aggregated results JSON file'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('results/figures'),
        help='Output directory for figures'
    )

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("HIGHER-ORDER FACTORIAL VISUALIZATION")
    print("=" * 70)
    print(f"Input file: {args.results_file}")
    print(f"Output directory: {args.output_dir}")
    print()

    # Load results
    print("📂 Loading aggregated results...")
    aggregated = load_aggregated_results(args.results_file)
    print(f"✅ Loaded {len(aggregated['experiments'])} experiments")
    print()

    # Generate figures
    print("🎨 Generating figures...")
    print()

    print("Figure 1: Hierarchical interaction decomposition...")
    create_hierarchical_decomposition_plot(aggregated, args.output_dir)

    print("Figure 2: Variance explained...")
    create_variance_explained_plot(aggregated, args.output_dir)

    print("Figure 3: 3-way surface plot...")
    create_3way_surface_plot(aggregated, args.output_dir)

    print("Figure 4: Interaction network diagram...")
    create_interaction_network_diagram(aggregated, args.output_dir)

    print()
    print("=" * 70)
    print("✅ VISUALIZATION COMPLETE")
    print("=" * 70)
    print(f"Generated 4 publication-quality figures (300 DPI)")
    print(f"Location: {args.output_dir}")
    print()
    print("Next steps:")
    print("  1. Review figures for accuracy")
    print("  2. Integrate into manuscript")
    print("  3. Finalize figure captions")
    print("  4. Submit for peer review")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
