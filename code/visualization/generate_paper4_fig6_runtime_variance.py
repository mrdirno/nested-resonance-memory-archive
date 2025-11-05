#!/usr/bin/env python3
"""
Paper 4 Figure 6 Generator: Runtime Variance Analysis

Purpose: Automated generation of Figure 6 from combined C186-C189 results
Visualizes computational runtime patterns across all experimental conditions

Figure Layout (2×2 grid):
- Panel A: Runtime distribution histogram (all experiments)
- Panel B: Runtime vs experimental condition (box plots)
- Panel C: CV scatter (population CV vs runtime CV)
- Panel D: Computational cost summary table

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
class ExperimentRuntimeData:
    """Runtime data for single experiment."""
    experiment_id: str
    runtimes: List[float]  # Minutes
    mean_runtime: float
    std_runtime: float
    cv_runtime: float
    min_runtime: float
    max_runtime: float


def load_experiment_results(results_path: Path) -> Optional[Dict]:
    """
    Load experimental results.

    Args:
        results_path: Path to results JSON

    Returns:
        Results dictionary or None if not available
    """
    if not results_path.exists():
        return None

    try:
        with open(results_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Error loading {results_path}: {e}")
        return None


def extract_runtime_data(
    exp_data: Dict,
    experiment_id: str
) -> Optional[ExperimentRuntimeData]:
    """
    Extract runtime data from experiment results.

    Args:
        exp_data: Experiment results dictionary
        experiment_id: Experiment identifier (C186, C187, etc.)

    Returns:
        ExperimentRuntimeData or None
    """
    experiments = exp_data.get('experiments', [])

    if not experiments:
        return None

    # Extract runtimes (convert seconds to minutes)
    runtimes = []
    for exp in experiments:
        runtime_sec = exp.get('runtime_seconds', None)
        if runtime_sec is not None:
            runtimes.append(runtime_sec / 60.0)

    if not runtimes:
        return None

    mean_rt = np.mean(runtimes)
    std_rt = np.std(runtimes)
    cv_rt = (std_rt / mean_rt) if mean_rt > 0 else 0

    return ExperimentRuntimeData(
        experiment_id=experiment_id,
        runtimes=runtimes,
        mean_runtime=mean_rt,
        std_runtime=std_rt,
        cv_runtime=cv_rt,
        min_runtime=np.min(runtimes),
        max_runtime=np.max(runtimes)
    )


def plot_runtime_distribution(
    ax: plt.Axes,
    all_runtime_data: List[ExperimentRuntimeData]
) -> None:
    """
    Plot Panel A: Runtime distribution histogram.

    Args:
        ax: Matplotlib axes
        all_runtime_data: List of runtime data for all experiments
    """
    # Combine all runtimes
    all_runtimes = []
    for data in all_runtime_data:
        all_runtimes.extend(data.runtimes)

    if not all_runtimes:
        ax.text(0.5, 0.5, 'No runtime data available',
                ha='center', va='center', transform=ax.transAxes)
        return

    # Histogram
    ax.hist(all_runtimes, bins=30, color='#2E86AB', alpha=0.7,
            edgecolor='black', linewidth=1.2)

    # Mean line
    mean_rt = np.mean(all_runtimes)
    ax.axvline(x=mean_rt, color='red', linestyle='--', linewidth=2,
               label=f'Mean: {mean_rt:.1f} min')

    ax.set_xlabel('Runtime (minutes)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=10, fontweight='bold')
    ax.set_title('(A) Runtime Distribution (All Experiments)', fontsize=11, fontweight='bold')

    ax.legend(fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='y')


def plot_runtime_by_experiment(
    ax: plt.Axes,
    all_runtime_data: List[ExperimentRuntimeData]
) -> None:
    """
    Plot Panel B: Runtime by experimental condition.

    Args:
        ax: Matplotlib axes
        all_runtime_data: List of runtime data for all experiments
    """
    if not all_runtime_data:
        ax.text(0.5, 0.5, 'No runtime data available',
                ha='center', va='center', transform=ax.transAxes)
        return

    # Box plot
    runtime_lists = [data.runtimes for data in all_runtime_data]
    labels = [data.experiment_id for data in all_runtime_data]

    bp = ax.boxplot(runtime_lists, labels=labels, patch_artist=True,
                    showmeans=True, meanline=True)

    # Color boxes
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_xlabel('Experiment', fontsize=10, fontweight='bold')
    ax.set_ylabel('Runtime (minutes)', fontsize=10, fontweight='bold')
    ax.set_title('(B) Runtime by Experimental Condition', fontsize=11, fontweight='bold')

    ax.grid(True, alpha=0.3, axis='y')


def plot_cv_correlation(
    ax: plt.Axes,
    all_runtime_data: List[ExperimentRuntimeData],
    c186_data: Optional[Dict],
    c187_data: Optional[Dict],
    c188_data: Optional[Dict],
    c189_data: Optional[Dict]
) -> None:
    """
    Plot Panel C: Population CV vs Runtime CV scatter.

    Args:
        ax: Matplotlib axes
        all_runtime_data: List of runtime data
        c186_data, c187_data, c188_data, c189_data: Experiment results
    """
    # Extract population CVs from experiments
    pop_cvs = []
    runtime_cvs = []
    labels = []

    for rt_data in all_runtime_data:
        # Get corresponding experiment data
        exp_id = rt_data.experiment_id
        exp_data_map = {
            'C186': c186_data,
            'C187': c187_data,
            'C188': c188_data,
            'C189': c189_data
        }

        exp_data = exp_data_map.get(exp_id)
        if not exp_data:
            continue

        experiments = exp_data.get('experiments', [])
        for exp in experiments:
            pop_stats = exp.get('population_stats', {})
            pop_cv = pop_stats.get('cv', 0.0) * 100  # Convert to percentage

            if pop_cv > 0:
                pop_cvs.append(pop_cv)
                runtime_cvs.append(rt_data.cv_runtime * 100)
                labels.append(exp_id)

    if not pop_cvs:
        ax.text(0.5, 0.5, 'Insufficient CV data',
                ha='center', va='center', transform=ax.transAxes)
        return

    # Scatter plot
    colors = {'C186': '#2E86AB', 'C187': '#A23B72',
              'C188': '#F18F01', 'C189': '#C73E1D'}

    for exp_id in set(labels):
        mask = [l == exp_id for l in labels]
        x = [p for p, m in zip(pop_cvs, mask) if m]
        y = [r for r, m in zip(runtime_cvs, mask) if m]

        ax.scatter(x, y, color=colors.get(exp_id, 'gray'),
                   label=exp_id, s=80, alpha=0.7, edgecolors='black')

    ax.set_xlabel('Population CV (%)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Runtime CV (%)', fontsize=10, fontweight='bold')
    ax.set_title('(C) Population vs Runtime Variance', fontsize=11, fontweight='bold')

    ax.legend(fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.3)


def plot_computational_cost_table(
    ax: plt.Axes,
    all_runtime_data: List[ExperimentRuntimeData]
) -> None:
    """
    Plot Panel D: Computational cost summary table.

    Args:
        ax: Matplotlib axes
        all_runtime_data: List of runtime data
    """
    ax.axis('off')

    # Title
    ax.text(0.5, 0.95, '(D) Computational Cost Summary',
            ha='center', va='top', fontsize=11, fontweight='bold',
            transform=ax.transAxes)

    # Table data
    table_data = []
    table_data.append(['Experiment', 'N', 'Mean (min)', 'SD (min)', 'CV (%)', 'Total (hr)'])

    total_runtime = 0.0
    total_experiments = 0

    for data in all_runtime_data:
        n = len(data.runtimes)
        mean_rt = data.mean_runtime
        sd_rt = data.std_runtime
        cv_rt = data.cv_runtime * 100
        total_rt = sum(data.runtimes) / 60.0  # Hours

        total_runtime += total_rt
        total_experiments += n

        table_data.append([
            data.experiment_id,
            str(n),
            f'{mean_rt:.1f}',
            f'{sd_rt:.1f}',
            f'{cv_rt:.1f}',
            f'{total_rt:.1f}'
        ])

    # Add total row
    table_data.append([
        'TOTAL',
        str(total_experiments),
        '-',
        '-',
        '-',
        f'{total_runtime:.1f}'
    ])

    # Create table
    table = ax.table(
        cellText=table_data,
        cellLoc='center',
        loc='center',
        bbox=[0.1, 0.1, 0.8, 0.75]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Style header row
    for i in range(len(table_data[0])):
        cell = table[(0, i)]
        cell.set_facecolor('#2E86AB')
        cell.set_text_props(weight='bold', color='white')

    # Style total row
    for i in range(len(table_data[0])):
        cell = table[(len(table_data)-1, i)]
        cell.set_facecolor('#F0F0F0')
        cell.set_text_props(weight='bold')

    # Alternating row colors
    for i in range(1, len(table_data)-1):
        for j in range(len(table_data[0])):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#F9F9F9')


def generate_figure6(
    c186_path: Path,
    c187_path: Path,
    c188_path: Path,
    c189_path: Path,
    output_path: Path,
    dpi: int = 300
) -> bool:
    """
    Generate Paper 4 Figure 6: Runtime Variance Analysis.

    Args:
        c186_path, c187_path, c188_path, c189_path: Paths to experiment results
        output_path: Path to save figure
        dpi: Resolution (default 300 for publication)

    Returns:
        True if successful
    """
    print("=" * 80)
    print("GENERATING PAPER 4 FIGURE 6: RUNTIME VARIANCE ANALYSIS")
    print("=" * 80)
    print()

    # Load all experiment data
    c186_data = load_experiment_results(c186_path)
    c187_data = load_experiment_results(c187_path)
    c188_data = load_experiment_results(c188_path)
    c189_data = load_experiment_results(c189_path)

    # Extract runtime data
    all_runtime_data = []

    if c186_data:
        rt_data = extract_runtime_data(c186_data, 'C186')
        if rt_data:
            all_runtime_data.append(rt_data)
            print(f"✓ C186: {len(rt_data.runtimes)} experiments, "
                  f"mean = {rt_data.mean_runtime:.1f} min")

    if c187_data:
        rt_data = extract_runtime_data(c187_data, 'C187')
        if rt_data:
            all_runtime_data.append(rt_data)
            print(f"✓ C187: {len(rt_data.runtimes)} experiments, "
                  f"mean = {rt_data.mean_runtime:.1f} min")

    if c188_data:
        rt_data = extract_runtime_data(c188_data, 'C188')
        if rt_data:
            all_runtime_data.append(rt_data)
            print(f"✓ C188: {len(rt_data.runtimes)} experiments, "
                  f"mean = {rt_data.mean_runtime:.1f} min")

    if c189_data:
        rt_data = extract_runtime_data(c189_data, 'C189')
        if rt_data:
            all_runtime_data.append(rt_data)
            print(f"✓ C189: {len(rt_data.runtimes)} experiments, "
                  f"mean = {rt_data.mean_runtime:.1f} min")

    if not all_runtime_data:
        print("⏳ No runtime data available. Skipping Figure 6 generation.")
        return False

    print()
    print(f"✓ Extracted runtime data from {len(all_runtime_data)} experiments")
    print()

    # Create figure (2×2 grid)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Figure 6: Computational Runtime Variance Analysis',
                 fontsize=14, fontweight='bold', y=0.995)

    # Panel A: Runtime distribution
    plot_runtime_distribution(axes[0, 0], all_runtime_data)

    # Panel B: Runtime by experiment
    plot_runtime_by_experiment(axes[0, 1], all_runtime_data)

    # Panel C: CV correlation
    plot_cv_correlation(axes[1, 0], all_runtime_data,
                        c186_data, c187_data, c188_data, c189_data)

    # Panel D: Cost table
    plot_computational_cost_table(axes[1, 1], all_runtime_data)

    # Layout
    plt.tight_layout(rect=[0, 0, 1, 0.99])

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ Figure 6 saved: {output_path}")
        print(f"  Resolution: {dpi} DPI")
        print(f"  Format: PNG")
        print()

        return True

    except Exception as e:
        print(f"Error saving Figure 6: {e}")
        plt.close()
        return False


def main():
    """Generate Figure 6 standalone."""

    c186_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json")
    c187_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json")
    c188_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json")
    c189_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json")
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig6_runtime_variance.png")

    success = generate_figure6(c186_path, c187_path, c188_path, c189_path,
                               output_path, dpi=300)

    if success:
        print("=" * 80)
        print("FIGURE 6 GENERATION COMPLETE")
        print("=" * 80)
    else:
        print("=" * 80)
        print("FIGURE 6 GENERATION SKIPPED (DATA PENDING)")
        print("=" * 80)


if __name__ == "__main__":
    main()
