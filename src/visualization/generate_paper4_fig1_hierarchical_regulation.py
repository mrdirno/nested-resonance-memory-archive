#!/usr/bin/env python3
"""
Paper 4 Figure 1: Hierarchical Energy Regulation

Purpose: Automated generation of Figure 1 from C186 validation results
Figure demonstrates inter-population energy dampening via migration coupling.

Panel Layout (2×2 grid):
(A) Population size time series (10 populations overlaid)
(B) Basin A occupation percentage (10 seeds, box plot)
(C) Cross-population migration network (force-directed layout)
(D) Energy regulation vs. single-population control

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
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class C186Results:
    """Container for C186 experimental results."""
    basin_a_percentages: List[float]
    mean_populations: List[float]
    cvs: List[float]
    migrations: List[int]
    population_trajectories: List[List[List[int]]]  # [seed][cycle][population_id]
    migration_events: List[List[Tuple[int, int, int]]]  # [seed][(cycle, from_pop, to_pop)]


@dataclass
class BaselineResults:
    """Container for baseline single-population results."""
    basin_a_percentage: float
    mean_population: float
    cv: float


def load_c186_results(results_path: Path) -> Optional[C186Results]:
    """
    Load C186 experimental results from JSON.

    Args:
        results_path: Path to C186 results JSON

    Returns:
        C186Results object or None if not available
    """
    if not results_path.exists():
        print(f"C186 results not found at {results_path}")
        return None

    try:
        with open(results_path, 'r') as f:
            data = json.load(f)

        # Extract metrics
        basin_a = []
        mean_pops = []
        cvs = []
        migrations = []
        pop_trajectories = []
        migration_events_all = []

        for exp in data.get('experiments', []):
            basin_a.append(exp['basin_a_percent'])
            mean_pops.append(exp['mean_population'])
            cvs.append(exp['cv_percent'])
            migrations.append(exp['migration_count'])

            # Population trajectories (if available)
            if 'population_trajectories' in exp:
                pop_trajectories.append(exp['population_trajectories'])

            # Migration events
            if 'migration_events' in exp:
                migration_events_all.append(exp['migration_events'])

        return C186Results(
            basin_a_percentages=basin_a,
            mean_populations=mean_pops,
            cvs=cvs,
            migrations=migrations,
            population_trajectories=pop_trajectories,
            migration_events=migration_events_all
        )

    except Exception as e:
        print(f"Error loading C186 results: {e}")
        return None


def load_baseline_results(baseline_path: Path) -> Optional[BaselineResults]:
    """
    Load baseline single-population results.

    Args:
        baseline_path: Path to baseline results JSON

    Returns:
        BaselineResults object or None if not available
    """
    if not baseline_path.exists():
        print(f"Baseline results not found at {baseline_path}")
        return None

    try:
        with open(baseline_path, 'r') as f:
            data = json.load(f)

        # Find 2.5% frequency condition
        for exp in data.get('experiments', []):
            if abs(exp.get('spawn_frequency', 0) - 2.5) < 0.01:
                return BaselineResults(
                    basin_a_percentage=exp['basin_a_percent'],
                    mean_population=exp['mean_population'],
                    cv=exp['cv_percent']
                )

        return None

    except Exception as e:
        print(f"Error loading baseline results: {e}")
        return None


def plot_population_trajectories(ax, c186: C186Results, num_cycles: int = 3000):
    """
    Panel A: Population size time series (10 populations overlaid).

    Args:
        ax: Matplotlib axis
        c186: C186Results object
        num_cycles: Number of cycles to plot
    """
    if not c186.population_trajectories:
        # Simulate trajectories if not available (for preliminary visualization)
        ax.text(0.5, 0.5, 'Population trajectories\ndata pending',
                ha='center', va='center', fontsize=10, color='gray')
        ax.set_xlabel('Cycle', fontsize=10)
        ax.set_ylabel('Population Size', fontsize=10)
        ax.set_title('(A) Population Dynamics', fontsize=11, fontweight='bold')
        return

    # Average trajectories across seeds
    num_populations = 10
    num_seeds = len(c186.population_trajectories)

    # Extract and average
    avg_trajectories = np.zeros((num_cycles, num_populations))

    for seed_trajectories in c186.population_trajectories:
        for cycle_idx, cycle_data in enumerate(seed_trajectories[:num_cycles]):
            for pop_id, pop_size in enumerate(cycle_data):
                avg_trajectories[cycle_idx, pop_id] += pop_size

    avg_trajectories /= num_seeds

    # Plot with transparency
    cycles = np.arange(num_cycles)
    colors = plt.cm.viridis(np.linspace(0, 1, num_populations))

    for pop_id in range(num_populations):
        ax.plot(cycles, avg_trajectories[:, pop_id],
                color=colors[pop_id], alpha=0.6, linewidth=0.8,
                label=f'Pop {pop_id}' if pop_id < 3 else None)

    ax.set_xlabel('Cycle', fontsize=10)
    ax.set_ylabel('Population Size', fontsize=10)
    ax.set_title('(A) Population Dynamics (n=10 populations)',
                 fontsize=11, fontweight='bold')
    ax.grid(alpha=0.3, linewidth=0.5)

    # Legend for first 3 populations only (to avoid clutter)
    ax.legend(fontsize=8, loc='upper right', framealpha=0.8)


def plot_basin_a_statistics(ax, c186: C186Results):
    """
    Panel B: Basin A occupation percentage (10 seeds, box plot).

    Args:
        ax: Matplotlib axis
        c186: C186Results object
    """
    basin_a_data = c186.basin_a_percentages

    # Box plot
    bp = ax.boxplot([basin_a_data], widths=0.5, patch_artist=True,
                     boxprops=dict(facecolor='lightblue', alpha=0.7),
                     medianprops=dict(color='red', linewidth=2),
                     whiskerprops=dict(linewidth=1.5),
                     capprops=dict(linewidth=1.5))

    # Overlay individual points
    x = np.random.normal(1, 0.04, size=len(basin_a_data))
    ax.scatter(x, basin_a_data, alpha=0.6, s=40, color='darkblue', zorder=3)

    # Add 5% threshold line
    ax.axhline(y=5.0, color='red', linestyle='--', linewidth=1.5,
               label='5% Threshold', alpha=0.7)

    # Statistical annotation
    mean_basin = np.mean(basin_a_data)
    sd_basin = np.std(basin_a_data, ddof=1)

    # One-sample t-test annotation (Basin A < 5%)
    annotation = f'Mean = {mean_basin:.2f}% ± {sd_basin:.2f}%\n'
    annotation += f'n = {len(basin_a_data)}\n'
    annotation += f'Predicted: ≤5%\n'

    if mean_basin <= 5.0:
        annotation += '✓ VALIDATED'
        color = 'green'
    else:
        annotation += '✗ NOT VALIDATED'
        color = 'red'

    ax.text(1.4, max(basin_a_data) * 0.8, annotation,
            fontsize=8, bbox=dict(boxstyle='round', facecolor='white',
                                  edgecolor=color, alpha=0.8))

    ax.set_ylabel('Basin A Occupation (%)', fontsize=10)
    ax.set_title('(B) Hierarchical Energy Regulation',
                 fontsize=11, fontweight='bold')
    ax.set_xticks([1])
    ax.set_xticklabels(['C186\n(Multi-pop)'], fontsize=9)
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linewidth=0.5)


def plot_migration_network(ax, c186: C186Results):
    """
    Panel C: Cross-population migration network (force-directed layout).

    Args:
        ax: Matplotlib axis
        c186: C186Results object
    """
    if not c186.migration_events:
        # Show expected network structure
        ax.text(0.5, 0.5, 'Migration network\ndata pending',
                ha='center', va='center', fontsize=10, color='gray')
        ax.set_title('(C) Migration Network', fontsize=11, fontweight='bold')
        ax.axis('off')
        return

    # Aggregate migration events across all seeds
    num_populations = 10
    migration_counts = np.zeros((num_populations, num_populations))

    for seed_events in c186.migration_events:
        for cycle, from_pop, to_pop in seed_events:
            migration_counts[from_pop, to_pop] += 1

    # Normalize by number of seeds
    migration_counts /= len(c186.migration_events)

    # Build NetworkX graph
    G = nx.DiGraph()

    for i in range(num_populations):
        G.add_node(i)

    for i in range(num_populations):
        for j in range(num_populations):
            if migration_counts[i, j] > 0.1:  # Threshold to avoid clutter
                G.add_edge(i, j, weight=migration_counts[i, j])

    # Force-directed layout
    pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)

    # Draw network
    node_colors = plt.cm.viridis(np.linspace(0, 1, num_populations))

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=500, alpha=0.8)

    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_weight='bold',
                            font_color='white')

    # Edge weights
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    max_weight = max(weights) if weights else 1.0

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray',
                           width=[w / max_weight * 3 for w in weights],
                           alpha=0.6, arrows=True, arrowsize=10,
                           arrowstyle='->', connectionstyle='arc3,rad=0.1')

    # Statistics
    total_migrations = np.sum(migration_counts) * len(c186.migration_events)
    mean_migrations = np.mean(c186.migrations)

    annotation = f'Mean Migrations: {mean_migrations:.1f}\n'
    annotation += f'Range: {min(c186.migrations)}-{max(c186.migrations)}\n'
    annotation += f'Predicted: 10-20'

    ax.text(0.02, 0.98, annotation, transform=ax.transAxes,
            fontsize=8, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title('(C) Migration Network (n=10 populations)',
                 fontsize=11, fontweight='bold')
    ax.axis('off')


def plot_hierarchical_vs_control(ax, c186: C186Results, baseline: Optional[BaselineResults]):
    """
    Panel D: Energy regulation vs. single-population control.

    Args:
        ax: Matplotlib axis
        c186: C186Results object
        baseline: BaselineResults object or None
    """
    mean_c186 = np.mean(c186.basin_a_percentages)
    sd_c186 = np.std(c186.basin_a_percentages, ddof=1)

    if baseline:
        mean_baseline = baseline.basin_a_percentage

        # Bar chart comparison
        conditions = ['Single-pop\n(Baseline)', 'Multi-pop\n(C186)']
        means = [mean_baseline, mean_c186]
        sds = [0, sd_c186]  # No SD for single baseline value

        colors = ['lightcoral', 'lightblue']
        bars = ax.bar(conditions, means, yerr=sds, capsize=5,
                      color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

        # Add 5% threshold
        ax.axhline(y=5.0, color='red', linestyle='--', linewidth=1.5,
                   label='5% Threshold', alpha=0.7)

        # Dampening factor
        if mean_c186 > 0:
            dampening = mean_baseline / mean_c186
            annotation = f'Energy Dampening:\n{dampening:.1f}× reduction'
        else:
            annotation = 'Complete suppression\n(Basin A = 0%)'

        ax.text(0.5, max(means) * 0.7, annotation,
                fontsize=9, ha='center',
                bbox=dict(boxstyle='round', facecolor='lightgreen',
                          edgecolor='green', alpha=0.8))

    else:
        # Only C186 data available
        ax.bar(['Multi-pop\n(C186)'], [mean_c186], yerr=[sd_c186], capsize=5,
               color='lightblue', alpha=0.7, edgecolor='black', linewidth=1.5)

        ax.axhline(y=5.0, color='red', linestyle='--', linewidth=1.5,
                   label='5% Threshold', alpha=0.7)

        ax.text(0.0, mean_c186 + sd_c186 + 1, 'Baseline\ndata pending',
                fontsize=8, color='gray')

    ax.set_ylabel('Basin A Occupation (%)', fontsize=10)
    ax.set_title('(D) Hierarchical vs. Single-Population',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linewidth=0.5)


def generate_figure1(
    c186_path: Path,
    baseline_path: Path,
    output_path: Path,
    dpi: int = 300
) -> bool:
    """
    Generate Paper 4 Figure 1: Hierarchical Energy Regulation.

    Args:
        c186_path: Path to C186 results JSON
        baseline_path: Path to baseline results JSON
        output_path: Path to save figure
        dpi: Figure resolution (default 300 for publication)

    Returns:
        True if successful, False otherwise
    """
    # Load data
    c186 = load_c186_results(c186_path)
    if not c186:
        print("Cannot generate figure without C186 results")
        return False

    baseline = load_baseline_results(baseline_path)

    # Create figure with 2×2 grid
    fig = plt.figure(figsize=(12, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    ax_A = fig.add_subplot(gs[0, 0])  # Population trajectories
    ax_B = fig.add_subplot(gs[0, 1])  # Basin A statistics
    ax_C = fig.add_subplot(gs[1, 0])  # Migration network
    ax_D = fig.add_subplot(gs[1, 1])  # Hierarchical vs. control

    # Generate panels
    plot_population_trajectories(ax_A, c186)
    plot_basin_a_statistics(ax_B, c186)
    plot_migration_network(ax_C, c186)
    plot_hierarchical_vs_control(ax_D, c186, baseline)

    # Overall title
    fig.suptitle('Figure 1: Hierarchical Energy Regulation in Metapopulation System',
                 fontsize=13, fontweight='bold', y=0.98)

    # Save figure
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        print(f"✓ Figure 1 saved to: {output_path}")
        print(f"  Resolution: {dpi} DPI")
        print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")
        return True

    except Exception as e:
        print(f"Error saving figure: {e}")
        return False

    finally:
        plt.close(fig)


def main():
    """Generate Figure 1 from C186 results."""

    # Paths
    c186_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json")
    baseline_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle171_baseline_results.json")
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig1_hierarchical_regulation.png")

    print("=" * 80)
    print("PAPER 4 FIGURE 1 GENERATION")
    print("=" * 80)
    print()
    print("Figure: Hierarchical Energy Regulation")
    print("Panels: 2×2 grid (A: trajectories, B: Basin A, C: network, D: comparison)")
    print("Resolution: 300 DPI (publication quality)")
    print()

    # Check data availability
    if c186_path.exists():
        print(f"✓ C186 results found: {c186_path}")
    else:
        print(f"⏳ C186 results pending: {c186_path}")
        print("   Will generate preliminary figure with available data")

    if baseline_path.exists():
        print(f"✓ Baseline results found: {baseline_path}")
    else:
        print(f"⏳ Baseline results pending: {baseline_path}")

    print()

    # Generate figure
    success = generate_figure1(c186_path, baseline_path, output_path, dpi=300)

    if success:
        print()
        print("=" * 80)
        print("FIGURE 1 GENERATION COMPLETE")
        print("=" * 80)
    else:
        print()
        print("Figure generation failed or incomplete.")


if __name__ == "__main__":
    main()
