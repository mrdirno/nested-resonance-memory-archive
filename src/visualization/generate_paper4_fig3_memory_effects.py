#!/usr/bin/env python3
"""
Paper 4 Figure 3 Generator: Memory Effects on Hierarchical Regulation

Purpose: Automated generation of Figure 3 from C188 experimental results
Visualizes impact of memory retention on energy regulation performance

Figure Layout (2×2 grid):
- Panel A: Basin A occupation vs memory depth
- Panel B: Migration count vs memory depth
- Panel C: Population CV vs memory depth
- Panel D: Mechanism diagram (depth → memory → regulation)

Target: Physical Review E standards (300 DPI, publication-ready)
Format: Single multi-panel figure with consistent styling

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1027
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MemoryConditionResults:
    """Results for single memory depth condition."""
    memory_depth: int
    basin_a_values: List[float]
    migration_counts: List[int]
    population_cvs: List[float]
    mean_basin_a: float
    mean_migrations: float
    mean_cv: float
    sem_basin_a: float
    sem_migrations: float
    sem_cv: float


def load_c188_results(results_path: Path) -> Optional[Dict]:
    """
    Load C188 experimental results.

    Args:
        results_path: Path to C188 results JSON

    Returns:
        Results dictionary or None if not available
    """
    if not results_path.exists():
        print(f"⏳ C188 results not available: {results_path}")
        return None

    try:
        with open(results_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading C188 results: {e}")
        return None


def extract_memory_condition_data(
    c188_data: Dict,
    memory_depth: int
) -> Optional[MemoryConditionResults]:
    """
    Extract data for specific memory depth condition.

    Args:
        c188_data: C188 experimental results
        memory_depth: Memory depth condition (1, 5, 10, 20)

    Returns:
        MemoryConditionResults or None
    """
    experiments = c188_data.get('experiments', [])

    # Filter to this memory depth
    condition_exps = [
        exp for exp in experiments
        if exp.get('memory_depth') == memory_depth
    ]

    if not condition_exps:
        return None

    # Extract metrics
    basin_a_values = [exp.get('basin_a_percent', 0.0) for exp in condition_exps]
    migration_counts = [exp.get('total_migrations', 0) for exp in condition_exps]

    # Calculate CVs from populations if available
    population_cvs = []
    for exp in condition_exps:
        pop_data = exp.get('population_stats', {})
        if 'cv' in pop_data:
            population_cvs.append(pop_data['cv'] * 100)  # Convert to percentage
        else:
            # Calculate from raw populations if needed
            pops = exp.get('final_populations', [])
            if pops:
                cv = (np.std(pops) / np.mean(pops)) if np.mean(pops) > 0 else 0
                population_cvs.append(cv * 100)

    if not population_cvs:
        population_cvs = [0.0] * len(basin_a_values)

    return MemoryConditionResults(
        memory_depth=memory_depth,
        basin_a_values=basin_a_values,
        migration_counts=migration_counts,
        population_cvs=population_cvs,
        mean_basin_a=np.mean(basin_a_values),
        mean_migrations=np.mean(migration_counts),
        mean_cv=np.mean(population_cvs),
        sem_basin_a=np.std(basin_a_values) / np.sqrt(len(basin_a_values)),
        sem_migrations=np.std(migration_counts) / np.sqrt(len(migration_counts)),
        sem_cv=np.std(population_cvs) / np.sqrt(len(population_cvs))
    )


def plot_basin_a_by_memory(
    ax: plt.Axes,
    conditions: List[MemoryConditionResults]
) -> None:
    """
    Plot Panel A: Basin A occupation vs memory depth.

    Args:
        ax: Matplotlib axes
        conditions: List of memory condition results
    """
    depths = [c.memory_depth for c in conditions]
    means = [c.mean_basin_a for c in conditions]
    sems = [c.sem_basin_a for c in conditions]

    # Line plot with error bars
    ax.errorbar(
        depths, means, yerr=sems,
        marker='o', markersize=8,
        linewidth=2, capsize=5,
        color='#2E86AB', label='Hierarchical System'
    )

    # Prediction threshold (Extension 2: ≤5%)
    ax.axhline(y=5.0, color='red', linestyle='--', linewidth=1.5,
               label='Predicted Threshold', alpha=0.7)

    ax.set_xlabel('Memory Depth (cycles)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Basin A Occupation (%)', fontsize=10, fontweight='bold')
    ax.set_title('(A) Energy Regulation vs Memory', fontsize=11, fontweight='bold')

    ax.legend(fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)

    # Format x-axis
    ax.set_xticks(depths)
    ax.set_xticklabels([str(d) for d in depths])


def plot_migrations_by_memory(
    ax: plt.Axes,
    conditions: List[MemoryConditionResults]
) -> None:
    """
    Plot Panel B: Migration count vs memory depth.

    Args:
        ax: Matplotlib axes
        conditions: List of memory condition results
    """
    depths = [c.memory_depth for c in conditions]
    means = [c.mean_migrations for c in conditions]
    sems = [c.sem_migrations for c in conditions]

    # Line plot with error bars
    ax.errorbar(
        depths, means, yerr=sems,
        marker='s', markersize=8,
        linewidth=2, capsize=5,
        color='#A23B72'
    )

    # Prediction range (Extension 2: 10-20)
    ax.axhspan(10, 20, color='green', alpha=0.1, label='Predicted Range')

    ax.set_xlabel('Memory Depth (cycles)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Total Migrations', fontsize=10, fontweight='bold')
    ax.set_title('(B) Migration Patterns vs Memory', fontsize=11, fontweight='bold')

    ax.legend(fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)

    # Format x-axis
    ax.set_xticks(depths)
    ax.set_xticklabels([str(d) for d in depths])


def plot_cv_by_memory(
    ax: plt.Axes,
    conditions: List[MemoryConditionResults]
) -> None:
    """
    Plot Panel C: Population CV vs memory depth.

    Args:
        ax: Matplotlib axes
        conditions: List of memory condition results
    """
    depths = [c.memory_depth for c in conditions]
    means = [c.mean_cv for c in conditions]
    sems = [c.sem_cv for c in conditions]

    # Line plot with error bars
    ax.errorbar(
        depths, means, yerr=sems,
        marker='^', markersize=8,
        linewidth=2, capsize=5,
        color='#F18F01'
    )

    ax.set_xlabel('Memory Depth (cycles)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Population CV (%)', fontsize=10, fontweight='bold')
    ax.set_title('(C) Variance Amplification vs Memory', fontsize=11, fontweight='bold')

    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)

    # Format x-axis
    ax.set_xticks(depths)
    ax.set_xticklabels([str(d) for d in depths])


def plot_memory_mechanism(ax: plt.Axes) -> None:
    """
    Plot Panel D: Memory mechanism diagram.

    Args:
        ax: Matplotlib axes
    """
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, '(D) Memory Mechanism',
            ha='center', va='top', fontsize=11, fontweight='bold')

    # Box 1: Memory Depth
    box1 = mpatches.FancyBboxPatch(
        (1, 6.5), 3, 1.5,
        boxstyle="round,pad=0.1",
        edgecolor='#2E86AB', facecolor='#D4E6F1',
        linewidth=2
    )
    ax.add_patch(box1)
    ax.text(2.5, 7.25, 'Memory Depth', ha='center', va='center',
            fontsize=9, fontweight='bold')
    ax.text(2.5, 6.75, '(pattern retention)', ha='center', va='center',
            fontsize=7, style='italic')

    # Arrow 1
    ax.annotate('', xy=(6, 7.25), xytext=(4.2, 7.25),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5.1, 7.6, 'enhances', ha='center', fontsize=7)

    # Box 2: Pattern Memory
    box2 = mpatches.FancyBboxPatch(
        (6, 6.5), 3, 1.5,
        boxstyle="round,pad=0.1",
        edgecolor='#A23B72', facecolor='#F8E5F1',
        linewidth=2
    )
    ax.add_patch(box2)
    ax.text(7.5, 7.25, 'Pattern Memory', ha='center', va='center',
            fontsize=9, fontweight='bold')
    ax.text(7.5, 6.75, '(composition history)', ha='center', va='center',
            fontsize=7, style='italic')

    # Arrow 2
    ax.annotate('', xy=(4.5, 5.5), xytext=(5.5, 6.3),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5.5, 5.9, 'improves', ha='center', fontsize=7, rotation=-45)

    # Box 3: Energy Regulation
    box3 = mpatches.FancyBboxPatch(
        (2.5, 4), 5, 1.5,
        boxstyle="round,pad=0.1",
        edgecolor='#F18F01', facecolor='#FEF5E7',
        linewidth=2
    )
    ax.add_patch(box3)
    ax.text(5, 4.75, 'Energy Regulation', ha='center', va='center',
            fontsize=9, fontweight='bold')
    ax.text(5, 4.25, '(Basin A suppression)', ha='center', va='center',
            fontsize=7, style='italic')

    # Prediction box
    pred_box = mpatches.FancyBboxPatch(
        (1.5, 1.5), 7, 2,
        boxstyle="round,pad=0.15",
        edgecolor='green', facecolor='#E8F8F5',
        linewidth=1.5, linestyle='--'
    )
    ax.add_patch(pred_box)

    ax.text(5, 3, 'Extension 2 Prediction:', ha='center', va='top',
            fontsize=8, fontweight='bold', color='darkgreen')
    ax.text(5, 2.5, 'Deeper memory → Stronger pattern retention →',
            ha='center', va='center', fontsize=7)
    ax.text(5, 2.1, 'More effective energy dampening',
            ha='center', va='center', fontsize=7)
    ax.text(5, 1.7, '(Basin A ≤ 5%, consistent migrations)',
            ha='center', va='center', fontsize=6, style='italic')


def generate_figure3(
    c188_path: Path,
    output_path: Path,
    dpi: int = 300
) -> bool:
    """
    Generate Paper 4 Figure 3: Memory Effects on Hierarchical Regulation.

    Args:
        c188_path: Path to C188 results JSON
        output_path: Path to save figure
        dpi: Resolution (default 300 for publication)

    Returns:
        True if successful
    """
    print("=" * 80)
    print("GENERATING PAPER 4 FIGURE 3: MEMORY EFFECTS")
    print("=" * 80)
    print()

    # Load data
    c188_data = load_c188_results(c188_path)

    if not c188_data:
        print("⏳ C188 data not available. Skipping Figure 3 generation.")
        return False

    print(f"✓ Loaded C188 results")
    print()

    # Extract memory conditions (Extension 2: depths = 1, 5, 10, 20)
    memory_depths = [1, 5, 10, 20]
    conditions = []

    for depth in memory_depths:
        cond_data = extract_memory_condition_data(c188_data, depth)
        if cond_data:
            conditions.append(cond_data)
            print(f"  Memory depth {depth:2d}: Basin A = {cond_data.mean_basin_a:.2f}%, "
                  f"Migrations = {cond_data.mean_migrations:.1f}, CV = {cond_data.mean_cv:.1f}%")

    if not conditions:
        print("Error: No valid memory conditions found")
        return False

    print()
    print(f"✓ Extracted {len(conditions)} memory conditions")
    print()

    # Create figure (2×2 grid)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Figure 3: Memory Effects on Hierarchical Energy Regulation',
                 fontsize=14, fontweight='bold', y=0.995)

    # Panel A: Basin A vs memory
    plot_basin_a_by_memory(axes[0, 0], conditions)

    # Panel B: Migrations vs memory
    plot_migrations_by_memory(axes[0, 1], conditions)

    # Panel C: CV vs memory
    plot_cv_by_memory(axes[1, 0], conditions)

    # Panel D: Mechanism diagram
    plot_memory_mechanism(axes[1, 1])

    # Layout
    plt.tight_layout(rect=[0, 0, 1, 0.99])

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ Figure 3 saved: {output_path}")
        print(f"  Resolution: {dpi} DPI")
        print(f"  Format: PNG")
        print()

        return True

    except Exception as e:
        print(f"Error saving Figure 3: {e}")
        plt.close()
        return False


def main():
    """Generate Figure 3 standalone."""

    c188_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json")
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig3_memory_effects.png")

    success = generate_figure3(c188_path, output_path, dpi=300)

    if success:
        print("=" * 80)
        print("FIGURE 3 GENERATION COMPLETE")
        print("=" * 80)
    else:
        print("=" * 80)
        print("FIGURE 3 GENERATION SKIPPED (DATA PENDING)")
        print("=" * 80)


if __name__ == "__main__":
    main()
