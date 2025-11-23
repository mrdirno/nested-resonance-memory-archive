#!/usr/bin/env python3
"""
C186 V1-V5 Publication Figure Generator
========================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-08 (Cycle 1279)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Purpose:
--------
Generate publication-quality figure showing linear scaling relationship
between spawn frequency and population size in hierarchical metapopulation
system (C186 V1-V5 experiments).

Figure Components:
------------------
- Scatter plot with error bars (95% CI)
- Linear regression fit
- Extrapolation to predicted critical frequency
- Basin A/B threshold line
- Publication-quality formatting (300 DPI)

Output:
-------
- c186_v1_v5_linear_scaling.png (300 DPI, publication-ready)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# ============================================================================
# CONFIGURATION
# ============================================================================

ANALYSIS_FILE = Path("/Volumes/dual/DUALITY-ZERO-V2/data/analysis/c186_v1_v5_comprehensive_analysis.json")
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASIN_A_THRESHOLD = 2.5
DPI = 300

# ============================================================================
# FIGURE GENERATION
# ============================================================================

def load_analysis_results():
    """Load pre-computed analysis results."""
    with open(ANALYSIS_FILE, 'r') as f:
        return json.load(f)

def create_figure(analysis_data):
    """Create publication-quality figure."""

    # Extract data
    experiments = analysis_data['experiment_details']
    regression = analysis_data['regression']
    critical_freq = analysis_data['critical_frequency']

    # Prepare data for plotting
    # Unique frequencies (average V1 and V2 which are both 2.5%)
    unique_data = {}
    for exp in experiments:
        f = exp['f_intra_pct']
        if f not in unique_data:
            unique_data[f] = []
        unique_data[f].append({
            'mean': exp['mean_population_avg'],
            'ci': exp['mean_population_95ci']
        })

    frequencies = []
    populations = []
    errors = []

    for f in sorted(unique_data.keys()):
        data_points = unique_data[f]
        mean_pop = np.mean([d['mean'] for d in data_points])
        # Propagate error (average of CIs)
        mean_ci = np.mean([d['ci'] for d in data_points])

        frequencies.append(f)
        populations.append(mean_pop)
        errors.append(mean_ci)

    frequencies = np.array(frequencies)
    populations = np.array(populations)
    errors = np.array(errors)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot data points with error bars
    ax.errorbar(frequencies, populations, yerr=errors,
                fmt='o', markersize=10, capsize=5, capthick=2,
                color='#2E86AB', ecolor='#A23B72', linewidth=2,
                label='Experimental Data')

    # Plot regression line
    slope = regression['slope']
    intercept = regression['intercept']
    r_squared = regression['r_squared']

    # Extend line to show extrapolation to critical frequency
    f_crit = critical_freq.get('predicted_f_crit_pct')
    if f_crit and f_crit > 0:
        x_fit = np.linspace(f_crit * 0.8, max(frequencies) * 1.1, 100)
    else:
        x_fit = np.linspace(0, max(frequencies) * 1.1, 100)

    y_fit = slope * x_fit + intercept

    ax.plot(x_fit, y_fit, '--', color='#F18F01', linewidth=2,
            label=f'Linear Fit: y = {slope:.2f}x + {intercept:.2f}\n(R² = {r_squared:.3f})')

    # Plot Basin A threshold
    ax.axhline(y=BASIN_A_THRESHOLD, color='#C73E1D', linestyle=':',
               linewidth=2, label=f'Basin A Threshold ({BASIN_A_THRESHOLD})')

    # Mark predicted critical frequency
    if f_crit and f_crit > 0:
        ax.axvline(x=f_crit, color='#6A994E', linestyle='-.', linewidth=2,
                   label=f'Predicted f_crit = {f_crit:.3f}%')
        ax.plot(f_crit, BASIN_A_THRESHOLD, 'D', markersize=12,
                color='#6A994E', markeredgecolor='black', markeredgewidth=1.5)

    # Formatting
    ax.set_xlabel('Intra-population Spawn Frequency (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Mean Population Size', fontsize=14, fontweight='bold')
    ax.set_title('Hierarchical Metapopulation: Linear Scaling of Population with Spawn Frequency\n' +
                 f'C186 V1-V5 (n=10 seeds each)', fontsize=16, fontweight='bold')

    ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')

    # Set axis limits
    ax.set_xlim(0 if not f_crit else f_crit * 0.7, max(frequencies) * 1.15)
    ax.set_ylim(0, max(populations) * 1.15)

    # Add text annotation with key results
    textstr = f'Hierarchical Advantage:\n' \
              f'• 100% Basin A viability (1.0-2.5%)\n' \
              f'• f_crit predicted: {f_crit:.3f}%\n' \
              f'• Single-scale f_crit ≈ 2.0%\n' \
              f'• Advantage: {2.0/f_crit:.1f}× lower threshold'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.65, 0.25, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props, family='monospace')

    plt.tight_layout()

    # Save figure
    output_file = OUTPUT_DIR / 'c186_v1_v5_linear_scaling.png'
    plt.savefig(output_file, dpi=DPI, bbox_inches='tight')
    print(f"✓ Figure saved: {output_file}")
    print(f"  Resolution: {DPI} DPI")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")

    plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 80)
    print("C186 V1-V5 FIGURE GENERATION")
    print("=" * 80)
    print()

    print("Loading analysis results...")
    analysis_data = load_analysis_results()
    print(f"✓ Loaded analysis for {len(analysis_data['experiment_details'])} experiments")
    print()

    print("Generating figure...")
    create_figure(analysis_data)
    print()

    print("=" * 80)
    print("FIGURE GENERATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
