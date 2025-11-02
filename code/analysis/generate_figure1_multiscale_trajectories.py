#!/usr/bin/env python3
"""
Generate Figure 1: Multi-Scale Timescale Validation Trajectories

Creates three-panel figure showing:
- Panel A: Spawn success percentage over time
- Panel B: Population size over time
- Panel C: Spawns per agent metric over time

Compares C176 V6 incremental validation (1000 cycles, individual seeds) with
C171 baseline (3000 cycles, mean).

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-02
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple

# Set publication-quality style
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

# Color scheme (colorblind-friendly)
COLORS = {
    'seed_42': '#1f77b4',      # Blue
    'seed_123': '#9467bd',     # Purple
    'seed_456': '#2ca02c',     # Green
    'seed_789': '#ff7f0e',     # Orange
    'seed_101': '#d62728',     # Red
    'c171_baseline': '#e377c2', # Pink
    'threshold_low': '#90ee90',  # Light green
    'threshold_mid': '#ffeb3b',  # Yellow
    'threshold_high': '#ff6b6b', # Light red
}


def load_c176_incremental_data(data_dir: Path) -> Dict:
    """
    Load C176 V6 incremental validation results.

    Args:
        data_dir: Path to data/results directory

    Returns:
        Dictionary with per-seed trajectories and statistics
    """
    filepath = data_dir / 'c176_v6_incremental_validation_results.json'

    if not filepath.exists():
        raise FileNotFoundError(f"C176 incremental data not found: {filepath}")

    with open(filepath, 'r') as f:
        data = json.load(f)

    return data


def load_c171_baseline_data(data_dir: Path) -> Dict:
    """
    Load C171 baseline results for comparison.

    Args:
        data_dir: Path to data/results directory

    Returns:
        Dictionary with mean trajectory and statistics
    """
    filepath = data_dir / 'c171_basin_stability_results.json'

    if not filepath.exists():
        raise FileNotFoundError(f"C171 baseline data not found: {filepath}")

    with open(filepath, 'r') as f:
        data = json.load(f)

    return data


def calculate_cumulative_spawn_success(spawn_attempts: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate cumulative spawn success rate over time.

    Args:
        spawn_attempts: List of spawn attempt records with 'cycle' and 'success' fields

    Returns:
        cycles (array): Cycle numbers
        success_rates (array): Cumulative success percentage at each cycle
    """
    if not spawn_attempts:
        return np.array([]), np.array([])

    # Sort by cycle
    attempts = sorted(spawn_attempts, key=lambda x: x['cycle'])

    cycles = []
    success_rates = []
    total_attempts = 0
    successful_attempts = 0

    for attempt in attempts:
        total_attempts += 1
        if attempt['success']:
            successful_attempts += 1

        cycles.append(attempt['cycle'])
        success_rates.append(100.0 * successful_attempts / total_attempts)

    return np.array(cycles), np.array(success_rates)


def calculate_spawns_per_agent(population_history: List[int], total_attempts: int,
                               max_cycle: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate spawns per agent metric over time.

    Args:
        population_history: List of population sizes at each cycle
        total_attempts: Total spawn attempts up to max_cycle
        max_cycle: Maximum cycle number

    Returns:
        cycles (array): Cycle numbers (checkpoint intervals)
        spawns_per_agent (array): Metric values at checkpoints
    """
    checkpoints = [100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000]
    checkpoints = [c for c in checkpoints if c <= max_cycle]

    cycles = []
    metric_values = []

    for checkpoint in checkpoints:
        if checkpoint <= len(population_history):
            # Calculate average population up to checkpoint
            avg_pop = np.mean(population_history[:checkpoint])

            # Spawns per agent (total attempts / avg population)
            if avg_pop > 0:
                metric = total_attempts / avg_pop
                cycles.append(checkpoint)
                metric_values.append(metric)

    return np.array(cycles), np.array(metric_values)


def create_figure1(c176_data: Dict, c171_data: Dict, output_path: Path):
    """
    Generate Figure 1: Multi-scale timescale validation trajectories.

    Args:
        c176_data: C176 V6 incremental validation data
        c171_data: C171 baseline data for comparison
        output_path: Where to save figure
    """
    # Create figure with 3 panels
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    fig.suptitle('Multi-Scale Timescale Validation: Non-Monotonic Spawn Success Pattern',
                 fontsize=14, fontweight='bold')

    # Panel A: Spawn success over time
    ax_success = axes[0]
    ax_success.set_xlabel('Cycle', fontsize=12)
    ax_success.set_ylabel('Spawn Success (%)', fontsize=12)
    ax_success.set_title('(A) Cumulative Spawn Success', fontsize=12, fontweight='bold')
    ax_success.grid(True, alpha=0.3, linestyle='--')
    ax_success.set_xlim(0, 1000)
    ax_success.set_ylim(0, 105)

    # Panel B: Population over time
    ax_population = axes[1]
    ax_population.set_xlabel('Cycle', fontsize=12)
    ax_population.set_ylabel('Population Size', fontsize=12)
    ax_population.set_title('(B) Population Growth', fontsize=12, fontweight='bold')
    ax_population.grid(True, alpha=0.3, linestyle='--')
    ax_population.set_xlim(0, 1000)
    ax_population.set_ylim(0, 28)

    # Panel C: Spawns per agent over time
    ax_metric = axes[2]
    ax_metric.set_xlabel('Cycle', fontsize=12)
    ax_metric.set_ylabel('Spawns / Agent', fontsize=12)
    ax_metric.set_title('(C) Spawns Per Agent Metric', fontsize=12, fontweight='bold')
    ax_metric.grid(True, alpha=0.3, linestyle='--')
    ax_metric.set_xlim(0, 1000)
    ax_metric.set_ylim(0, 12)

    # Add threshold zones to Panel C
    ax_metric.axhspan(0, 2, alpha=0.1, color=COLORS['threshold_low'], label='High success (<2)')
    ax_metric.axhspan(2, 4, alpha=0.1, color=COLORS['threshold_mid'], label='Transition (2-4)')
    ax_metric.axhspan(4, 12, alpha=0.1, color=COLORS['threshold_high'], label='Low success (>4)')
    ax_metric.axhline(y=2, color='green', linestyle='--', linewidth=1.5, alpha=0.7)
    ax_metric.axhline(y=4, color='red', linestyle='--', linewidth=1.5, alpha=0.7)

    # Plot C176 V6 individual seeds
    seed_names = {42: 'Seed 42', 123: 'Seed 123', 456: 'Seed 456',
                  789: 'Seed 789', 101: 'Seed 101'}
    seed_colors = {42: COLORS['seed_42'], 123: COLORS['seed_123'],
                   456: COLORS['seed_456'], 789: COLORS['seed_789'],
                   101: COLORS['seed_101']}

    for seed_result in c176_data.get('results', []):
        seed = seed_result['seed']

        # Panel A: Spawn success trajectory
        if 'spawn_attempts' in seed_result:
            cycles, success_rates = calculate_cumulative_spawn_success(
                seed_result['spawn_attempts']
            )
            ax_success.plot(cycles, success_rates,
                          color=seed_colors.get(seed, 'black'),
                          label=seed_names.get(seed, f'Seed {seed}'),
                          linewidth=2, alpha=0.8)

        # Panel B: Population trajectory
        if 'population_trajectory' in seed_result:
            pop_trajectory = seed_result['population_trajectory']
            cycles = np.arange(len(pop_trajectory))
            ax_population.plot(cycles, pop_trajectory,
                             color=seed_colors.get(seed, 'black'),
                             label=seed_names.get(seed, f'Seed {seed}'),
                             linewidth=2, alpha=0.8)

        # Panel C: Spawns per agent trajectory
        if 'population_trajectory' in seed_result and 'total_spawn_attempts' in seed_result:
            cycles, metric_values = calculate_spawns_per_agent(
                seed_result['population_trajectory'],
                seed_result['total_spawn_attempts'],
                1000
            )
            ax_metric.plot(cycles, metric_values,
                         color=seed_colors.get(seed, 'black'),
                         label=seed_names.get(seed, f'Seed {seed}'),
                         linewidth=2, alpha=0.8, marker='o', markersize=4)

    # Plot C171 baseline (3000 cycles, show only up to 1000 for comparison)
    if 'summary_statistics' in c171_data:
        c171_stats = c171_data['summary_statistics']

        # C171 final values (at 3000 cycles, shown at x=1000 for visual comparison)
        c171_success = c171_stats.get('mean_spawn_success', 0.23) * 100
        c171_population = c171_stats.get('mean_final_population', 17.4)
        c171_spawns_per_agent = c171_stats.get('mean_spawns_per_agent', 8.38)

        # Show C171 as horizontal reference line (represents long-term outcome)
        ax_success.axhline(y=c171_success, color=COLORS['c171_baseline'],
                          linestyle=':', linewidth=2.5,
                          label='C171 (3000 cycles, 23%)', alpha=0.9)

        ax_population.axhline(y=c171_population, color=COLORS['c171_baseline'],
                            linestyle=':', linewidth=2.5,
                            label='C171 (3000 cycles)', alpha=0.9)

        ax_metric.axhline(y=c171_spawns_per_agent, color=COLORS['c171_baseline'],
                         linestyle=':', linewidth=2.5,
                         label='C171 (3000 cycles)', alpha=0.9)

    # Add legends
    ax_success.legend(loc='lower left', framealpha=0.9)
    ax_population.legend(loc='upper left', framealpha=0.9)
    ax_metric.legend(loc='upper left', framealpha=0.9, fontsize=8)

    # Add four-phase annotations to Panel A
    ax_success.annotate('Phase 1:\nInitial decline', xy=(125, 93), fontsize=8,
                       ha='center', va='top', color='darkred',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    ax_success.annotate('Phase 2:\nStabilization', xy=(375, 85), fontsize=8,
                       ha='center', va='top', color='darkblue',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    ax_success.annotate('Phase 3:\nRecovery', xy=(625, 87), fontsize=8,
                       ha='center', va='top', color='darkgreen',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    ax_success.annotate('Phase 4:\nStrong recovery', xy=(875, 91), fontsize=8,
                       ha='center', va='top', color='darkgreen', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Figure 1 saved: {output_path}")
    print(f"  Resolution: 300 DPI")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    plt.close()


def main():
    """Main execution function."""
    # Set paths
    repo_root = Path(__file__).parent.parent.parent
    data_dir = repo_root / 'data' / 'results'
    output_dir = repo_root / 'data' / 'figures'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("GENERATING FIGURE 1: Multi-Scale Timescale Validation Trajectories")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    try:
        c176_data = load_c176_incremental_data(data_dir)
        n_seeds = len(c176_data.get('results', []))
        print(f"  ✓ C176 V6 incremental data loaded ({n_seeds} seeds)")
    except FileNotFoundError as e:
        print(f"  ⚠ Warning: {e}")
        print(f"  Using placeholder C176 data")
        c176_data = {'results': []}

    try:
        c171_data = load_c171_baseline_data(data_dir)
        print(f"  ✓ C171 baseline data loaded")
    except FileNotFoundError as e:
        print(f"  ⚠ Warning: {e}")
        print(f"  Using placeholder C171 data")
        c171_data = {'summary_statistics': {
            'mean_spawn_success': 0.23,
            'mean_final_population': 17.4,
            'mean_spawns_per_agent': 8.38
        }}

    print()

    # Generate figure
    print("Generating figure...")
    output_path = output_dir / 'fig1_multiscale_trajectories_300dpi.png'
    create_figure1(c176_data, c171_data, output_path)

    print()
    print("=" * 80)
    print("FIGURE GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Review figure visually for clarity")
    print("  2. Verify all seeds plotted correctly")
    print("  3. Check color scheme is colorblind-friendly")
    print("  4. Confirm resolution is 300 DPI")
    print("  5. Update manuscript with figure reference")
    print()


if __name__ == '__main__':
    main()
