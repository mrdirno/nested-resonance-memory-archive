#!/usr/bin/env python3
"""
Comprehensive Visualization for C186 Hierarchical Advantage Discovery
Generates multi-panel publication figure integrating V1-V8 results

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1078)
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from pathlib import Path

# Color scheme (consistent with graphical abstract)
COLOR_SINGLE = '#2E86C1'       # Blue for single-scale
COLOR_HIERARCHICAL = '#27AE60'  # Green for hierarchical
COLOR_FAILURE = '#E74C3C'       # Red for failure
COLOR_SUCCESS = '#27AE60'       # Green for success
COLOR_TEXT = '#2C3E50'          # Dark gray text
COLOR_BG = '#F8F9F9'            # Light gray background

def load_c186_results():
    """Load all available C186 experiment results"""
    results_dir = Path('/Volumes/dual/DUALITY-ZERO-V2/data/results')

    results = {
        'v1_hierarchical': None,
        'v2_hierarchical': None,
        'v3_single_scale': None,
        'v4_migration_variation': None,
        'v5_linear_scaling': None,
        'v6_ultra_low_freq': None,
        'v7_migration_rates': None,
        'v8_population_counts': None
    }

    # V1: Hierarchical spawn failure (Basin B demonstration)
    v1_path = results_dir / 'c186_v1_hierarchical_spawn_failure_results.json'
    if v1_path.exists():
        with open(v1_path) as f:
            results['v1_hierarchical'] = json.load(f)

    # V2: Hierarchical spawn success (Basin A demonstration)
    v2_path = results_dir / 'c186_v2_hierarchical_spawn_success_results.json'
    if v2_path.exists():
        with open(v2_path) as f:
            results['v2_hierarchical'] = json.load(f)

    # V3: Single-scale frequency sweep
    v3_path = results_dir / 'c186_v3_single_scale_frequency_sweep_results.json'
    if v3_path.exists():
        with open(v3_path) as f:
            results['v3_single_scale'] = json.load(f)

    # V4: Migration rate variation
    v4_path = results_dir / 'c186_v4_migration_rate_variation_results.json'
    if v4_path.exists():
        with open(v4_path) as f:
            results['v4_migration_variation'] = json.load(f)

    # V5: Linear scaling validation
    v5_path = results_dir / 'c186_v5_linear_scaling_validation_results.json'
    if v5_path.exists():
        with open(v5_path) as f:
            results['v5_linear_scaling'] = json.load(f)

    # V6: Ultra-low frequency boundary test (may not exist yet)
    v6_path = results_dir / 'c186_v6_ultra_low_frequency_results.json'
    if v6_path.exists():
        with open(v6_path) as f:
            results['v6_ultra_low_freq'] = json.load(f)

    # V7: Migration rate sweep (future)
    v7_path = results_dir / 'c186_v7_migration_rate_sweep_results.json'
    if v7_path.exists():
        with open(v7_path) as f:
            results['v7_migration_rates'] = json.load(f)

    # V8: Population count variation (future)
    v8_path = results_dir / 'c186_v8_population_count_variation_results.json'
    if v8_path.exists():
        with open(v8_path) as f:
            results['v8_population_counts'] = json.load(f)

    return results


def extract_basin_classification(results_v5):
    """Extract basin classification from V5 linear scaling data"""
    experiments = results_v5['experiments']
    frequencies = []
    mean_pops = []
    basins = []

    for exp in experiments:
        freq = exp['parameters']['spawn_frequency']
        seeds_data = exp['seeds']

        # Calculate mean population across seeds
        final_pops = [seed['final_population'] for seed in seeds_data]
        mean_pop = np.mean(final_pops)

        # Classify basin (threshold = 2.5 agents)
        basin = 'A' if mean_pop > 2.5 else 'B'

        frequencies.append(freq)
        mean_pops.append(mean_pop)
        basins.append(basin)

    return frequencies, mean_pops, basins


def plot_panel_a_basin_transition(ax, results):
    """Panel A: Basin transition and critical frequency identification"""
    if results['v5_linear_scaling'] is None:
        ax.text(0.5, 0.5, 'V5 Data Pending', ha='center', va='center',
                fontsize=12, color=COLOR_TEXT)
        ax.set_title('Panel A: Basin Transition', fontsize=11, fontweight='bold')
        return

    frequencies, mean_pops, basins = extract_basin_classification(results['v5_linear_scaling'])

    # Plot population vs frequency with basin colors
    for freq, pop, basin in zip(frequencies, mean_pops, basins):
        color = COLOR_SUCCESS if basin == 'A' else COLOR_FAILURE
        ax.scatter(freq * 100, pop, s=100, c=color, alpha=0.7, edgecolors='black', linewidth=1)

    # Add basin threshold line
    ax.axhline(y=2.5, color='gray', linestyle='--', linewidth=1.5, alpha=0.5, label='Basin Threshold')

    # Add critical frequency region
    f_crit_single = 6.25  # From V3
    ax.axvline(x=f_crit_single, color=COLOR_SINGLE, linestyle=':', linewidth=2, label='Single-Scale f_crit')

    ax.set_xlabel('Spawn Frequency (%)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Mean Final Population', fontsize=10, fontweight='bold')
    ax.set_title('Panel A: Basin Transition', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)


def plot_panel_b_critical_frequency_comparison(ax, results):
    """Panel B: Bar chart comparing critical frequencies"""
    # Single-scale critical frequency from V3
    f_crit_single = 6.25  # ~every 16 cycles

    # Hierarchical critical frequency (estimated from V5, V6 will refine)
    # From V5: 1.0% achieves homeostasis
    f_crit_hier = 1.0  # Will be refined by V6

    # If V6 available, use actual critical frequency
    if results['v6_ultra_low_freq'] is not None:
        # Extract actual critical frequency from V6
        # (placeholder - actual implementation depends on V6 structure)
        pass

    # Bar positions
    x = np.arange(2)
    widths = [f_crit_single, f_crit_hier]
    colors = [COLOR_SINGLE, COLOR_HIERARCHICAL]
    labels = ['Single-Scale', 'Hierarchical']

    bars = ax.bar(x, widths, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for i, (bar, width) in enumerate(zip(bars, widths)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{width:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add alpha annotation
    alpha = f_crit_hier / f_crit_single
    ax.text(0.5, max(widths) * 0.8, f'α = {alpha:.2f}',
            ha='center', va='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.6))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax.set_ylabel('Critical Spawn Frequency (%)', fontsize=10, fontweight='bold')
    ax.set_title('Panel B: Critical Frequency Comparison', fontsize=11, fontweight='bold')
    ax.set_ylim(0, max(widths) * 1.2)
    ax.grid(True, axis='y', alpha=0.3)


def plot_panel_c_linear_scaling(ax, results):
    """Panel C: Linear scaling relationship"""
    if results['v5_linear_scaling'] is None:
        ax.text(0.5, 0.5, 'V5 Data Pending', ha='center', va='center',
                fontsize=12, color=COLOR_TEXT)
        ax.set_title('Panel C: Linear Scaling', fontsize=11, fontweight='bold')
        return

    frequencies, mean_pops, basins = extract_basin_classification(results['v5_linear_scaling'])

    # Filter Basin A only for regression
    basin_a_freq = [f for f, b in zip(frequencies, basins) if b == 'A']
    basin_a_pop = [p for p, b in zip(mean_pops, basins) if b == 'A']

    # Scatter plot
    for freq, pop, basin in zip(frequencies, mean_pops, basins):
        color = COLOR_SUCCESS if basin == 'A' else COLOR_FAILURE
        marker = 'o' if basin == 'A' else 'x'
        ax.scatter(freq * 100, pop, s=80, c=color, marker=marker, alpha=0.7,
                  edgecolors='black', linewidth=1)

    # Linear regression on Basin A
    if len(basin_a_freq) > 1:
        coeffs = np.polyfit([f * 100 for f in basin_a_freq], basin_a_pop, 1)
        slope, intercept = coeffs

        # Fit line
        x_fit = np.array(basin_a_freq) * 100
        y_fit = slope * x_fit + intercept
        ax.plot(x_fit, y_fit, color=COLOR_HIERARCHICAL, linewidth=2.5,
               label=f'y = {slope:.2f}x + {intercept:.2f}')

        # R² calculation
        residuals = np.array(basin_a_pop) - (slope * x_fit + intercept)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((np.array(basin_a_pop) - np.mean(basin_a_pop))**2)
        r_squared = 1 - (ss_res / ss_tot)

        # Add R² annotation
        ax.text(0.05, 0.95, f'R² = {r_squared:.4f}', transform=ax.transAxes,
               fontsize=10, fontweight='bold', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    ax.set_xlabel('Spawn Frequency (%)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Mean Final Population', fontsize=10, fontweight='bold')
    ax.set_title('Panel C: Linear Scaling (Basin A)', fontsize=11, fontweight='bold')
    ax.legend(loc='lower right', fontsize=8)
    ax.grid(True, alpha=0.3)


def plot_panel_d_migration_sensitivity(ax, results):
    """Panel D: Migration rate sensitivity (V4 or V7 data)"""
    if results['v4_migration_variation'] is None and results['v7_migration_rates'] is None:
        ax.text(0.5, 0.5, 'V4/V7 Data Pending', ha='center', va='center',
                fontsize=12, color=COLOR_TEXT)
        ax.set_title('Panel D: Migration Sensitivity', fontsize=11, fontweight='bold')
        return

    # Use V4 data if available (preliminary), else V7
    data = results['v4_migration_variation'] or results['v7_migration_rates']

    # Extract migration rates and population outcomes
    experiments = data['experiments']
    migration_rates = []
    mean_pops = []

    for exp in experiments:
        mig_rate = exp['parameters']['migration_frequency']
        seeds_data = exp['seeds']
        final_pops = [seed['final_population'] for seed in seeds_data]
        mean_pop = np.mean(final_pops)

        migration_rates.append(mig_rate * 100)
        mean_pops.append(mean_pop)

    # Plot
    ax.plot(migration_rates, mean_pops, 'o-', color=COLOR_HIERARCHICAL,
           linewidth=2, markersize=8, markeredgecolor='black', markeredgewidth=1)

    # Highlight optimal region (0.5%)
    optimal_idx = np.argmax(mean_pops)
    optimal_rate = migration_rates[optimal_idx]
    optimal_pop = mean_pops[optimal_idx]

    ax.scatter([optimal_rate], [optimal_pop], s=200, c='yellow', marker='*',
              edgecolors='black', linewidths=2, zorder=5, label='Optimal')

    ax.set_xlabel('Migration Frequency (%)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Mean Final Population', fontsize=10, fontweight='bold')
    ax.set_title('Panel D: Migration Sensitivity', fontsize=11, fontweight='bold')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)


def generate_comprehensive_figure(results):
    """Generate comprehensive 4-panel publication figure"""
    fig = plt.figure(figsize=(14, 10), dpi=300, facecolor=COLOR_BG)
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    plot_panel_a_basin_transition(ax_a, results)
    plot_panel_b_critical_frequency_comparison(ax_b, results)
    plot_panel_c_linear_scaling(ax_c, results)
    plot_panel_d_migration_sensitivity(ax_d, results)

    # Overall title
    fig.suptitle('C186 Hierarchical Advantage Discovery: Comprehensive Results',
                fontsize=14, fontweight='bold', y=0.98)

    # Save figure
    output_path = '/Volumes/dual/DUALITY-ZERO-V2/data/figures/c186_comprehensive_results.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=COLOR_BG)
    print(f"Comprehensive figure saved: {output_path}")

    plt.close()

    return output_path


def print_data_availability_summary(results):
    """Print summary of available data"""
    print("\n" + "="*70)
    print("C186 DATA AVAILABILITY SUMMARY")
    print("="*70)

    variants = [
        ('V1: Hierarchical Spawn Failure', 'v1_hierarchical'),
        ('V2: Hierarchical Spawn Success', 'v2_hierarchical'),
        ('V3: Single-Scale Frequency Sweep', 'v3_single_scale'),
        ('V4: Migration Rate Variation', 'v4_migration_variation'),
        ('V5: Linear Scaling Validation', 'v5_linear_scaling'),
        ('V6: Ultra-Low Frequency Boundary', 'v6_ultra_low_freq'),
        ('V7: Migration Rate Sweep', 'v7_migration_rates'),
        ('V8: Population Count Variation', 'v8_population_counts')
    ]

    for label, key in variants:
        status = '✅ AVAILABLE' if results[key] is not None else '⏳ PENDING'
        print(f"  {label}: {status}")

        if results[key] is not None:
            n_exp = len(results[key].get('experiments', []))
            print(f"    → {n_exp} experiments")

    print("="*70 + "\n")


if __name__ == '__main__':
    print("="*70)
    print("C186 Comprehensive Visualization Generator")
    print("="*70)
    print()

    # Load all available results
    print("Loading C186 experiment results...")
    results = load_c186_results()

    # Print data availability
    print_data_availability_summary(results)

    # Generate comprehensive figure
    print("Generating comprehensive 4-panel figure...")
    output_path = generate_comprehensive_figure(results)

    print("\n" + "="*70)
    print("Comprehensive Visualization Complete")
    print("="*70)
    print(f"Output: {output_path}")
    print("\nFigure Panels:")
    print("  Panel A: Basin transition and critical frequency")
    print("  Panel B: Critical frequency comparison (α coefficient)")
    print("  Panel C: Linear scaling relationship (R²)")
    print("  Panel D: Migration sensitivity analysis")
    print("\nSpecifications:")
    print("  - Resolution: 300 DPI")
    print("  - Format: PNG")
    print("  - Color scheme: Consistent with graphical abstract")
    print("\nNext Steps:")
    print("  - Regenerate when V6 completes (refine f_crit_hier)")
    print("  - Regenerate when V7/V8 complete (enhance Panel D)")
    print("  - Integrate into manuscript figures")
    print("="*70)
