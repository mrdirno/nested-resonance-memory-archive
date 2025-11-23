#!/usr/bin/env python3
"""
Generate Figure 2: Spawns Per Agent Threshold Model

Creates scatter plot showing relationship between spawns/agent metric and
spawn success rate, comparing C171 baseline (n=40, 3000 cycles) with C176 V6
incremental validation (n=5, 1000 cycles).

Visualizes three empirical threshold zones:
- <2 spawns/agent: High success (70-100%)
- 2-4 spawns/agent: Transition zone (40-70%)
- >4 spawns/agent: Low success (20-30%)

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
from scipy import stats

# Set publication-quality style
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 9

# Color scheme
COLORS = {
    'c171_points': '#1f77b4',      # Blue dots (n=40)
    'c176_points': '#d62728',      # Red stars (n=5)
    'threshold_low': '#90ee90',    # Light green (<2)
    'threshold_mid': '#ffeb3b',    # Yellow (2-4)
    'threshold_high': '#ffcccb',   # Light red (>4)
    'regression': '#2ca02c',       # Green
}


def load_c176_incremental_data(data_dir: Path) -> Dict:
    """Load C176 V6 incremental validation results."""
    filepath = data_dir / 'c176_v6_incremental_validation_results.json'

    if not filepath.exists():
        raise FileNotFoundError(f"C176 data not found: {filepath}")

    with open(filepath, 'r') as f:
        data = json.load(f)

    return data


def load_c171_baseline_data(data_dir: Path) -> Dict:
    """Load C171 baseline results."""
    filepath = data_dir / 'c171_basin_stability_results.json'

    if not filepath.exists():
        raise FileNotFoundError(f"C171 data not found: {filepath}")

    with open(filepath, 'r') as f:
        data = json.load(f)

    return data


def calculate_spawns_per_agent(population_trajectory: List[int],
                               total_spawn_attempts: int) -> float:
    """
    Calculate spawns per agent metric.

    Args:
        population_trajectory: Population size at each cycle
        total_spawn_attempts: Total number of spawn attempts

    Returns:
        Spawns per agent ratio
    """
    if not population_trajectory:
        return 0.0

    avg_population = np.mean(population_trajectory)

    if avg_population == 0:
        return 0.0

    return total_spawn_attempts / avg_population


def extract_c171_points(c171_data: Dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract spawns/agent and success rate for all C171 trajectories.

    Args:
        c171_data: C171 baseline data

    Returns:
        spawns_per_agent (array): Metric values for each trajectory
        success_rates (array): Success percentages for each trajectory
    """
    spawns_per_agent = []
    success_rates = []

    for result in c171_data.get('results', []):
        if 'population_trajectory' in result and 'total_spawn_attempts' in result:
            metric = calculate_spawns_per_agent(
                result['population_trajectory'],
                result['total_spawn_attempts']
            )
            spawns_per_agent.append(metric)

            # Convert success rate to percentage
            success = result.get('spawn_success', 0.0)
            if success <= 1.0:  # If in decimal form
                success *= 100.0
            success_rates.append(success)

    return np.array(spawns_per_agent), np.array(success_rates)


def extract_c176_points(c176_data: Dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract spawns/agent and success rate for all C176 V6 seeds.

    Args:
        c176_data: C176 V6 incremental validation data

    Returns:
        spawns_per_agent (array): Metric values for each seed
        success_rates (array): Success percentages for each seed
    """
    spawns_per_agent = []
    success_rates = []

    for result in c176_data.get('results', []):
        if 'population_trajectory' in result and 'total_spawn_attempts' in result:
            metric = calculate_spawns_per_agent(
                result['population_trajectory'],
                result['total_spawn_attempts']
            )
            spawns_per_agent.append(metric)

            # Convert success rate to percentage
            success = result.get('spawn_success', 0.0)
            if success <= 1.0:  # If in decimal form
                success *= 100.0
            success_rates.append(success)

    return np.array(spawns_per_agent), np.array(success_rates)


def calculate_regression_by_zone(spawns_per_agent: np.ndarray,
                                 success_rates: np.ndarray,
                                 zone_min: float, zone_max: float) -> Dict:
    """
    Calculate linear regression for points within a threshold zone.

    Args:
        spawns_per_agent: All x values
        success_rates: All y values
        zone_min: Minimum spawns/agent for zone
        zone_max: Maximum spawns/agent for zone

    Returns:
        Dictionary with slope, intercept, r_value, p_value
    """
    # Filter points in zone
    mask = (spawns_per_agent >= zone_min) & (spawns_per_agent < zone_max)
    x_zone = spawns_per_agent[mask]
    y_zone = success_rates[mask]

    if len(x_zone) < 2:
        return {'slope': 0, 'intercept': 0, 'r_value': 0, 'p_value': 1.0, 'n': 0}

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_zone, y_zone)

    return {
        'slope': slope,
        'intercept': intercept,
        'r_value': r_value,
        'p_value': p_value,
        'n': len(x_zone)
    }


def create_figure2(c171_data: Dict, c176_data: Dict, output_path: Path):
    """
    Generate Figure 2: Spawns per agent threshold model.

    Args:
        c171_data: C171 baseline data (n=40, 3000 cycles)
        c176_data: C176 V6 incremental data (n=5, 1000 cycles)
        output_path: Where to save figure
    """
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    fig.suptitle('Spawns Per Agent Metric Unifies Spawn Success Across Timescales',
                 fontsize=14, fontweight='bold')

    ax.set_xlabel('Spawns Per Agent (total attempts / average population)', fontsize=12)
    ax.set_ylabel('Spawn Success (%)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 105)

    # Add threshold zones as background shading
    ax.axvspan(0, 2, alpha=0.15, color=COLORS['threshold_low'], zorder=1,
              label='High success zone (<2)')
    ax.axvspan(2, 4, alpha=0.15, color=COLORS['threshold_mid'], zorder=1,
              label='Transition zone (2-4)')
    ax.axvspan(4, 14, alpha=0.15, color=COLORS['threshold_high'], zorder=1,
              label='Low success zone (>4)')

    # Add threshold boundary lines
    ax.axvline(x=2, color='green', linestyle='--', linewidth=2, alpha=0.7, zorder=2)
    ax.axvline(x=4, color='red', linestyle='--', linewidth=2, alpha=0.7, zorder=2)

    # Extract C171 points (n=40, 3000 cycles)
    c171_x, c171_y = extract_c171_points(c171_data)

    if len(c171_x) > 0:
        ax.scatter(c171_x, c171_y, c=COLORS['c171_points'], marker='o',
                  s=80, alpha=0.7, edgecolors='black', linewidth=0.5,
                  label=f'C171 baseline (n={len(c171_x)}, 3000 cycles)',
                  zorder=3)

        # Add statistics annotation for C171
        c171_mean_x = np.mean(c171_x)
        c171_mean_y = np.mean(c171_y)
        c171_sd_x = np.std(c171_x)
        c171_sd_y = np.std(c171_y)

        print(f"C171 statistics:")
        print(f"  Spawns/agent: {c171_mean_x:.2f} ± {c171_sd_x:.2f}")
        print(f"  Success rate: {c171_mean_y:.1f}% ± {c171_sd_y:.1f}%")
        print(f"  n = {len(c171_x)}")

    # Extract C176 points (n=5, 1000 cycles)
    c176_x, c176_y = extract_c176_points(c176_data)

    if len(c176_x) > 0:
        ax.scatter(c176_x, c176_y, c=COLORS['c176_points'], marker='*',
                  s=400, alpha=0.9, edgecolors='black', linewidth=1.5,
                  label=f'C176 incremental (n={len(c176_x)}, 1000 cycles)',
                  zorder=4)

        # Add error bars for C176 (mean ± SD)
        c176_mean_x = np.mean(c176_x)
        c176_mean_y = np.mean(c176_y)
        c176_sd_x = np.std(c176_x)
        c176_sd_y = np.std(c176_y)

        ax.errorbar(c176_mean_x, c176_mean_y,
                   xerr=c176_sd_x, yerr=c176_sd_y,
                   fmt='none', ecolor=COLORS['c176_points'],
                   capsize=5, capthick=2, alpha=0.7, zorder=4)

        print(f"\nC176 V6 statistics:")
        print(f"  Spawns/agent: {c176_mean_x:.2f} ± {c176_sd_x:.2f}")
        print(f"  Success rate: {c176_mean_y:.1f}% ± {c176_sd_y:.1f}%")
        print(f"  n = {len(c176_x)}")

    # Calculate and plot regression lines by zone (using C171 data)
    if len(c171_x) > 0:
        zones = [
            (0, 2, 'High', COLORS['threshold_low']),
            (2, 4, 'Transition', COLORS['threshold_mid']),
            (4, 14, 'Low', COLORS['threshold_high'])
        ]

        for zone_min, zone_max, zone_name, zone_color in zones:
            reg = calculate_regression_by_zone(c171_x, c171_y, zone_min, zone_max)

            if reg['n'] >= 2:
                # Generate regression line
                x_line = np.linspace(zone_min, zone_max, 100)
                y_line = reg['slope'] * x_line + reg['intercept']

                # Clip to zone
                y_line = np.clip(y_line, 0, 100)

                ax.plot(x_line, y_line, color=zone_color, linestyle='-',
                       linewidth=2.5, alpha=0.8, zorder=2)

                # Add R² annotation
                r_squared = reg['r_value'] ** 2
                p_stars = '***' if reg['p_value'] < 0.001 else \
                         ('**' if reg['p_value'] < 0.01 else \
                         ('*' if reg['p_value'] < 0.05 else 'ns'))

                mid_x = (zone_min + zone_max) / 2
                mid_y = reg['slope'] * mid_x + reg['intercept']

                ax.annotate(f'{zone_name} zone\nR²={r_squared:.3f}{p_stars}\nn={reg["n"]}',
                           xy=(mid_x, mid_y), fontsize=8,
                           ha='center', va='bottom',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='white', alpha=0.8, edgecolor=zone_color))

                print(f"\n{zone_name} zone regression:")
                print(f"  R² = {r_squared:.3f}")
                print(f"  p = {reg['p_value']:.4f} {p_stars}")
                print(f"  n = {reg['n']}")

    # Add key findings annotation
    annotation_text = (
        "KEY FINDING:\n"
        "• C171 (3000 cycles) clusters at high spawns/agent (~8.4) → low success (~23%)\n"
        "• C176 (1000 cycles) at threshold boundary (~2.0) → high success (~90%)\n"
        "• Population-mediated recovery reduces constraint at intermediate timescale"
    )

    ax.text(0.98, 0.02, annotation_text,
           transform=ax.transAxes,
           fontsize=9, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                    alpha=0.9, edgecolor='black'))

    # Legend
    ax.legend(loc='upper right', framealpha=0.95, fontsize=9)

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"\n✓ Figure 2 saved: {output_path}")
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
    print("GENERATING FIGURE 2: Spawns Per Agent Threshold Model")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    try:
        c171_data = load_c171_baseline_data(data_dir)
        n_c171 = len(c171_data.get('results', []))
        print(f"  ✓ C171 baseline data loaded ({n_c171} trajectories)")
    except FileNotFoundError as e:
        print(f"  ⚠ Warning: {e}")
        print(f"  Using placeholder C171 data")
        c171_data = {'results': []}

    try:
        c176_data = load_c176_incremental_data(data_dir)
        n_c176 = len(c176_data.get('results', []))
        print(f"  ✓ C176 V6 incremental data loaded ({n_c176} seeds)")
    except FileNotFoundError as e:
        print(f"  ⚠ Warning: {e}")
        print(f"  Using placeholder C176 data")
        c176_data = {'results': []}

    print()

    # Generate figure
    print("Generating figure...")
    output_path = output_dir / 'fig2_threshold_scatter_300dpi.png'
    create_figure2(c171_data, c176_data, output_path)

    print()
    print("=" * 80)
    print("FIGURE GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Review figure visually for clarity")
    print("  2. Verify threshold zones clearly visible")
    print("  3. Check C171 and C176 points distinguishable")
    print("  4. Confirm statistical annotations accurate")
    print("  5. Verify resolution is 300 DPI")
    print("  6. Update manuscript with figure reference")
    print()


if __name__ == '__main__':
    main()
