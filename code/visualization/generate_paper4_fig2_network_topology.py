#!/usr/bin/env python3
"""
Paper 4 Figure 2: Network Structure Effects

Purpose: Automated generation of Figure 2 from C187 validation results
Figure demonstrates how network topology modulates hierarchical dynamics.

Panel Layout (3×2 grid):
(A-C) Population dynamics for 3 topologies (ring, star, fully-connected)
(D-F) Basin A statistics by topology (bar charts with error bars)

Specifications: PAPER4_FIGURE_SPECIFICATIONS.md
Target Resolution: 300 DPI
Publication Standards: Physical Review E format

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1024
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import networkx as nx
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from scipy import stats


@dataclass
class TopologyResults:
    """Container for topology-specific results."""
    topology_name: str
    basin_a_percentages: List[float]
    mean_populations: List[float]
    cvs: List[float]
    migrations: List[int]


def load_c187_results(results_path: Path) -> Optional[Dict[str, TopologyResults]]:
    """
    Load C187 experimental results from JSON.

    Args:
        results_path: Path to C187 results JSON

    Returns:
        Dictionary mapping topology names to TopologyResults
    """
    if not results_path.exists():
        print(f"C187 results not found at {results_path}")
        return None

    try:
        with open(results_path, 'r') as f:
            data = json.load(f)

        topology_data = {}

        for exp in data.get('experiments', []):
            topology = exp['topology']

            if topology not in topology_data:
                topology_data[topology] = {
                    'basin_a': [],
                    'mean_pop': [],
                    'cv': [],
                    'migrations': []
                }

            topology_data[topology]['basin_a'].append(exp['basin_a_percent'])
            topology_data[topology]['mean_pop'].append(exp['mean_population'])
            topology_data[topology]['cv'].append(exp['cv_percent'])
            topology_data[topology]['migrations'].append(exp['migration_count'])

        # Convert to TopologyResults objects
        results = {}
        for topology, metrics in topology_data.items():
            results[topology] = TopologyResults(
                topology_name=topology,
                basin_a_percentages=metrics['basin_a'],
                mean_populations=metrics['mean_pop'],
                cvs=metrics['cv'],
                migrations=metrics['migrations']
            )

        return results

    except Exception as e:
        print(f"Error loading C187 results: {e}")
        return None


def draw_topology_diagram(ax, topology_name: str, num_nodes: int = 10):
    """
    Draw network topology diagram.

    Args:
        ax: Matplotlib axis
        topology_name: Name of topology (ring, star, fully_connected)
        num_nodes: Number of nodes
    """
    G = nx.Graph()

    for i in range(num_nodes):
        G.add_node(i)

    # Build edges based on topology
    if topology_name == "ring":
        for i in range(num_nodes):
            G.add_edge(i, (i + 1) % num_nodes)
        pos = nx.circular_layout(G)

    elif topology_name == "star":
        center = 0
        for i in range(1, num_nodes):
            G.add_edge(center, i)
        pos = nx.spring_layout(G, seed=42)

    elif topology_name == "fully_connected":
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                G.add_edge(i, j)
        pos = nx.circular_layout(G)

    else:
        # Default layout
        pos = nx.spring_layout(G, seed=42)

    # Draw
    node_colors = plt.cm.viridis(np.linspace(0, 1, num_nodes))

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=300, alpha=0.8, edgecolors='black',
                           linewidths=1.5)

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray',
                           width=1.5, alpha=0.6)

    # Add topology name
    ax.text(0.5, 1.05, topology_name.replace('_', ' ').title(),
            transform=ax.transAxes, fontsize=10,
            ha='center', fontweight='bold')

    ax.axis('off')


def plot_topology_dynamics(ax, results: TopologyResults, topology_name: str):
    """
    Panels A-C: Population dynamics for each topology.

    Args:
        ax: Matplotlib axis
        results: TopologyResults object
        topology_name: Topology name for title
    """
    # Since we don't have full trajectories, show summary statistics
    mean_basin = np.mean(results.basin_a_percentages)
    sd_basin = np.std(results.basin_a_percentages, ddof=1)

    mean_cv = np.mean(results.cvs)
    sd_cv = np.std(results.cvs, ddof=1)

    mean_mig = np.mean(results.migrations)
    sd_mig = np.std(results.migrations, ddof=1)

    # Create mini topology diagram at top
    inset_ax = ax.inset_axes([0.7, 0.7, 0.25, 0.25])
    draw_topology_diagram(inset_ax, topology_name, num_nodes=6)

    # Display key metrics as text
    metrics_text = f"Basin A: {mean_basin:.1f}% ± {sd_basin:.1f}%\n"
    metrics_text += f"CV: {mean_cv:.1f}% ± {sd_cv:.1f}%\n"
    metrics_text += f"Migrations: {mean_mig:.1f} ± {sd_mig:.1f}\n"
    metrics_text += f"n = {len(results.basin_a_percentages)}"

    ax.text(0.5, 0.5, metrics_text, transform=ax.transAxes,
            fontsize=11, ha='center', va='center',
            bbox=dict(boxstyle='round', facecolor='white',
                      edgecolor='gray', alpha=0.9, linewidth=1.5))

    ax.set_title(f"({chr(65 + ['ring', 'star', 'fully_connected'].index(topology_name))}) "
                 f"{topology_name.replace('_', ' ').title()}",
                 fontsize=11, fontweight='bold')
    ax.axis('off')


def plot_topology_basin_a(ax, all_results: Dict[str, TopologyResults], topology_order: List[str]):
    """
    Panels D-F: Basin A statistics by topology.

    Args:
        ax: Matplotlib axis
        all_results: Dictionary of all topology results
        topology_order: Order of topologies for display
    """
    means = []
    sds = []
    labels = []

    for topology in topology_order:
        if topology in all_results:
            results = all_results[topology]
            means.append(np.mean(results.basin_a_percentages))
            sds.append(np.std(results.basin_a_percentages, ddof=1))
            labels.append(topology.replace('_', '\n').title())
        else:
            means.append(0)
            sds.append(0)
            labels.append(topology.replace('_', '\n').title() + '\n(pending)')

    # Bar chart
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, orange, green
    bars = ax.bar(labels, means, yerr=sds, capsize=5,
                   color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add 5% threshold
    ax.axhline(y=5.0, color='red', linestyle='--', linewidth=1.5,
               label='5% Threshold', alpha=0.7)

    # Statistical comparison (ANOVA)
    if len([r for r in all_results.values() if r.basin_a_percentages]) >= 2:
        groups = [r.basin_a_percentages for r in all_results.values()
                  if r.basin_a_percentages]

        f_stat, p_value = stats.f_oneway(*groups)

        annotation = f'One-way ANOVA:\nF = {f_stat:.2f}, p = {p_value:.4f}'

        if p_value < 0.05:
            annotation += '\n*** Significant'
            color = 'green'
        else:
            annotation += '\nNot significant'
            color = 'gray'

        ax.text(0.02, 0.98, annotation, transform=ax.transAxes,
                fontsize=8, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white',
                          edgecolor=color, alpha=0.8))

    ax.set_ylabel('Basin A Occupation (%)', fontsize=10)
    ax.set_title('(D-F) Topology Effect on Energy Regulation',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linewidth=0.5)


def generate_figure2(
    c187_path: Path,
    output_path: Path,
    dpi: int = 300
) -> bool:
    """
    Generate Paper 4 Figure 2: Network Structure Effects.

    Args:
        c187_path: Path to C187 results JSON
        output_path: Path to save figure
        dpi: Figure resolution (default 300 for publication)

    Returns:
        True if successful, False otherwise
    """
    # Load data
    results = load_c187_results(c187_path)
    if not results:
        print("Cannot generate figure without C187 results")
        return False

    topology_order = ["ring", "star", "fully_connected"]

    # Create figure with 2×2 grid (A-C top row, D bottom spanning)
    fig = plt.figure(figsize=(15, 8))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3,
                           height_ratios=[1, 1])

    # Top row: Individual topology metrics
    axes_top = [fig.add_subplot(gs[0, i]) for i in range(3)]

    # Bottom row: Comparative bar chart (spanning all columns)
    ax_bottom = fig.add_subplot(gs[1, :])

    # Generate panels
    for i, topology in enumerate(topology_order):
        if topology in results:
            plot_topology_dynamics(axes_top[i], results[topology], topology)
        else:
            axes_top[i].text(0.5, 0.5, f'{topology.replace("_", " ").title()}\ndata pending',
                             ha='center', va='center', fontsize=10, color='gray',
                             transform=axes_top[i].transAxes)
            axes_top[i].set_title(f"({chr(65 + i)}) {topology.replace('_', ' ').title()}",
                                  fontsize=11, fontweight='bold')
            axes_top[i].axis('off')

    plot_topology_basin_a(ax_bottom, results, topology_order)

    # Overall title
    fig.suptitle('Figure 2: Network Topology Effects on Hierarchical Dynamics',
                 fontsize=13, fontweight='bold', y=0.98)

    # Save figure
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        print(f"✓ Figure 2 saved to: {output_path}")
        print(f"  Resolution: {dpi} DPI")
        print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")
        return True

    except Exception as e:
        print(f"Error saving figure: {e}")
        return False

    finally:
        plt.close(fig)


def main():
    """Generate Figure 2 from C187 results."""

    # Paths
    c187_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json")
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig2_network_topology.png")

    print("=" * 80)
    print("PAPER 4 FIGURE 2 GENERATION")
    print("=" * 80)
    print()
    print("Figure: Network Topology Effects")
    print("Panels: 3×2 grid (A-C: topologies, D-F: comparison)")
    print("Resolution: 300 DPI (publication quality)")
    print()

    # Check data availability
    if c187_path.exists():
        print(f"✓ C187 results found: {c187_path}")
    else:
        print(f"⏳ C187 results pending: {c187_path}")
        print("   Will generate preliminary figure when data available")
        return

    print()

    # Generate figure
    success = generate_figure2(c187_path, output_path, dpi=300)

    if success:
        print()
        print("=" * 80)
        print("FIGURE 2 GENERATION COMPLETE")
        print("=" * 80)
    else:
        print()
        print("Figure generation failed or incomplete.")


if __name__ == "__main__":
    main()
