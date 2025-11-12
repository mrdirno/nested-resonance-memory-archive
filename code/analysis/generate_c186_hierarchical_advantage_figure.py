#!/usr/bin/env python3
"""
C186 Hierarchical Advantage Figure Generator
=============================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-09 (Cycle 1336)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Purpose:
--------
Generate publication-quality figure showing hierarchical advantage (α = 607)
from C186 V1-V5 experimental data using authoritative campaign analysis.

Figure Components:
------------------
1. Linear scaling: Population vs. spawn frequency
2. Hierarchical advantage coefficient α = 607
3. Extrapolated critical frequency
4. Basin A threshold
5. Publication-quality formatting (300 DPI)

Output:
-------
- c186_hierarchical_advantage.png (300 DPI, publication-ready)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# ============================================================================
# CONFIGURATION
# ============================================================================

CAMPAIGN_FILE = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_campaign_analysis.json")
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASIN_A_THRESHOLD = 2.5  # Population threshold for Basin A classification
SINGLE_SCALE_CRITICAL_F = 0.04  # 4% from previous experiments
DPI = 300

# ============================================================================
# FIGURE GENERATION
# ============================================================================

def load_campaign_data():
    """Load authoritative campaign analysis."""
    with open(CAMPAIGN_FILE, 'r') as f:
        return json.load(f)

def create_figure(campaign_data):
    """Create publication-quality hierarchical advantage figure."""

    # Extract data from campaign analysis
    freq_data = campaign_data['frequency_response_analysis']
    frequencies = np.array(freq_data['frequencies_tested'])  # [0.01, 0.015, 0.02, 0.025, 0.05]
    populations = np.array(freq_data['mean_populations'])

    # Extract fitted parameters
    slope, intercept = freq_data['linear_fit_coeffs']  # [3004.25, 19.80]
    r_squared = freq_data['linear_fit_r2']  # 0.9999987
    alpha = freq_data['hierarchical_advantage_alpha']  # 607.1
    f_crit_hier = freq_data['critical_frequency_estimate']  # 6.59e-05 (0.0066%)
    f_crit_single = freq_data['single_scale_critical_f']  # 0.04 (4.0%)

    # Create figure with two subplots
    fig = plt.figure(figsize=(14, 6))

    # ========================================================================
    # SUBPLOT 1: Linear Scaling
    # ========================================================================
    ax1 = plt.subplot(1, 2, 1)

    # Convert frequencies to percentage for display
    freq_pct = frequencies * 100

    # Plot data points
    ax1.plot(freq_pct, populations, 'o', markersize=12,
             color='#2E86AB', markeredgecolor='black', markeredgewidth=1.5,
             label='C186 V1-V5 Data', zorder=3)

    # Plot regression line
    freq_fit = np.linspace(0, max(frequencies) * 1.1, 100)
    pop_fit = slope * freq_fit + intercept
    ax1.plot(freq_fit * 100, pop_fit, '--', color='#F18F01', linewidth=2.5,
             label=f'Linear Fit: Pop = {slope:.1f}×f + {intercept:.1f}\n(R² = {r_squared:.6f})',
             zorder=2)

    # Plot Basin A threshold
    ax1.axhline(y=BASIN_A_THRESHOLD, color='#C73E1D', linestyle=':',
                linewidth=2, alpha=0.7, label=f'Basin A Threshold = {BASIN_A_THRESHOLD}',
                zorder=1)

    # Mark extrapolated critical frequency
    ax1.axvline(x=f_crit_hier * 100, color='#6A994E', linestyle='-.',
                linewidth=2, alpha=0.7,
                label=f'Hierarchical f_crit = {f_crit_hier*100:.4f}%\n(extrapolated)',
                zorder=1)

    # Formatting
    ax1.set_xlabel('Spawn Frequency (%)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Mean Population Size', fontsize=13, fontweight='bold')
    ax1.set_title('Linear Population Scaling\n(Hierarchical Metapopulation)',
                  fontsize=14, fontweight='bold', pad=15)

    ax1.legend(loc='upper left', fontsize=10, framealpha=0.95)
    ax1.grid(True, alpha=0.3, linestyle='--', zorder=0)

    # Set limits
    ax1.set_xlim(-0.2, max(freq_pct) * 1.1)
    ax1.set_ylim(0, max(populations) * 1.15)

    # Add statistics box
    textstr = f'V1-V5 Statistics:\n' \
              f'• Frequencies: {min(freq_pct):.1f}% - {max(freq_pct):.1f}%\n' \
              f'• Populations: {min(populations):.1f} - {max(populations):.1f}\n' \
              f'• 100% Basin A (10/10 seeds each)\n' \
              f'• Perfect linearity (R²≈1.000)'

    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8, pad=0.6)
    ax1.text(0.98, 0.35, textstr, transform=ax1.transAxes, fontsize=9,
             verticalalignment='top', horizontalalignment='right',
             bbox=props, family='monospace')

    # ========================================================================
    # SUBPLOT 2: Hierarchical Advantage
    # ========================================================================
    ax2 = plt.subplot(1, 2, 2)

    # Create bar chart comparing critical frequencies
    systems = ['Hierarchical\n(C186 V1-V5)', 'Single-Scale\n(Prior Work)']
    f_crits = [f_crit_hier * 100, f_crit_single * 100]
    colors = ['#6A994E', '#C73E1D']

    bars = ax2.bar(systems, f_crits, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=2)

    # Add value labels on bars
    for bar, f_crit in zip(bars, f_crits):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{f_crit:.4f}%', ha='center', va='bottom',
                fontsize=11, fontweight='bold')

    # Draw arrow showing advantage
    arrow_y = max(f_crits) * 0.6
    ax2.annotate('', xy=(0.9, arrow_y), xytext=(1.1, arrow_y),
                arrowprops=dict(arrowstyle='<->', lw=3, color='purple'))

    ax2.text(1.0, arrow_y + 0.2, f'α = {alpha:.1f}×\nAdvantage',
            ha='center', va='bottom', fontsize=12, fontweight='bold',
            color='purple',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

    # Formatting
    ax2.set_ylabel('Critical Spawn Frequency (%)', fontsize=13, fontweight='bold')
    ax2.set_title('Hierarchical Advantage Coefficient\n(α = f_single / f_hier)',
                  fontsize=14, fontweight='bold', pad=15)
    ax2.set_ylim(0, max(f_crits) * 1.3)
    ax2.grid(axis='y', alpha=0.3, linestyle='--', zorder=0)

    # Add advantage explanation box
    advantage_text = f'Hierarchical Advantage:\n\n' \
                     f'α = f_crit(single) / f_crit(hier)\n' \
                     f'α = {f_crit_single*100:.2f}% / {f_crit_hier*100:.4f}%\n' \
                     f'α = {alpha:.1f}\n\n' \
                     f'Hierarchical system requires\n' \
                     f'{alpha:.0f}× LOWER spawn frequency\n' \
                     f'to maintain homeostasis'

    props = dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, pad=0.8)
    ax2.text(0.5, 0.95, advantage_text, transform=ax2.transAxes, fontsize=10,
             verticalalignment='top', horizontalalignment='center',
             bbox=props, family='monospace', fontweight='bold')

    # ========================================================================
    # FIGURE-LEVEL FORMATTING
    # ========================================================================

    fig.suptitle('C186: Hierarchical Compartmentalization Reduces Critical Frequencies\n' +
                 'Energy-Constrained Metapopulation Dynamics (n=10 seeds per frequency)',
                 fontsize=15, fontweight='bold', y=1.00)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save figure
    output_file = OUTPUT_DIR / 'c186_hierarchical_advantage.png'
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
    print("C186 HIERARCHICAL ADVANTAGE FIGURE GENERATION")
    print("=" * 80)
    print()

    print("Loading campaign analysis...")
    campaign_data = load_campaign_data()
    print(f"✓ Loaded campaign: {campaign_data['campaign']}")
    print(f"  Variants completed: {campaign_data['variants_completed']}/{campaign_data['variants_total']}")
    print(f"  Hierarchical advantage: α = {campaign_data['key_findings']['hierarchical_advantage_alpha']:.1f}")
    print()

    print("Generating publication figure...")
    create_figure(campaign_data)
    print()

    print("=" * 80)
    print("FIGURE GENERATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
