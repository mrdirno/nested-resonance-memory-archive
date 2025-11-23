#!/usr/bin/env python3
"""
Generate Publication Figure: Hierarchical Stability (C189 Data)

Purpose:
  Visualize hierarchical vs. flat system stability using variance comparison
  from c189_statistical_analysis.json data.

Key Finding:
  Hierarchical systems exhibit ZERO variance (SD = 0.0) across all frequencies
  vs. flat systems (SD = 3-9), with highly significant differences (p < 0.003).

Interpretation:
  Hierarchical architecture provides robustness through STABILITY, not just
  mean performance improvement.

Figure Components:
  Panel A: Mean population comparison (bar plot with error bars)
  Panel B: Variance comparison (hierarchical vs. flat SD)
  Panel C: Statistical significance (Levene test p-values)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-09 (Cycle 1339)
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Load C189 statistical analysis data
DATA_PATH = Path(__file__).parent.parent.parent / "experiments" / "results" / "c189_statistical_analysis.json"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "c189_hierarchical_stability.png"

def load_c189_data():
    """Load C189 statistical analysis results."""
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

def create_figure(data):
    """Create publication-quality three-panel figure."""

    # Extract data for each frequency
    frequencies = ['0.5', '1.0', '1.5', '2.0']
    freq_labels = ['0.5%', '1.0%', '1.5%', '2.0%']

    hier_means = []
    hier_stds = []
    flat_means = []
    flat_stds = []
    levene_pvals = []

    for freq in frequencies:
        freq_data = data['test_results_by_frequency'][freq]
        hier_means.append(freq_data['hierarchical_mean'])
        hier_stds.append(freq_data['hierarchical_std'])
        flat_means.append(freq_data['flat_mean'])
        flat_stds.append(freq_data['flat_std'])
        levene_pvals.append(freq_data['levene_p_value'])

    # Create figure with 3 panels
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Hierarchical Stability: Zero-Variance Regime in Energy-Regulated Systems',
                 fontsize=14, fontweight='bold', y=1.02)

    x = np.arange(len(frequencies))
    width = 0.35

    # Panel A: Mean Population Comparison
    ax = axes[0]
    bars1 = ax.bar(x - width/2, hier_means, width,
                   yerr=hier_stds, capsize=5,
                   label='Hierarchical', color='#2E86AB', alpha=0.8,
                   error_kw={'linewidth': 1.5})
    bars2 = ax.bar(x + width/2, flat_means, width,
                   yerr=flat_stds, capsize=5,
                   label='Flat', color='#A23B72', alpha=0.8,
                   error_kw={'linewidth': 1.5})

    ax.set_xlabel('Spawn Frequency (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Mean Population', fontsize=11, fontweight='bold')
    ax.set_title('A. Population Comparison', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(freq_labels)
    ax.legend(frameon=True, shadow=True, fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add value labels on bars
    for i, (h, f) in enumerate(zip(hier_means, flat_means)):
        ax.text(i - width/2, h + 1, f'{h:.0f}', ha='center', va='bottom', fontsize=9)
        ax.text(i + width/2, f + 1, f'{f:.1f}', ha='center', va='bottom', fontsize=9)

    # Panel B: Variance Comparison (Standard Deviation)
    ax = axes[1]
    bars1 = ax.bar(x - width/2, hier_stds, width,
                   label='Hierarchical', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, flat_stds, width,
                   label='Flat', color='#A23B72', alpha=0.8)

    ax.set_xlabel('Spawn Frequency (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Standard Deviation', fontsize=11, fontweight='bold')
    ax.set_title('B. Stability Comparison (Variance)', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(freq_labels)
    ax.legend(frameon=True, shadow=True, fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add value labels
    for i, (h, f) in enumerate(zip(hier_stds, flat_stds)):
        ax.text(i - width/2, h + 0.2, f'{h:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2E86AB')
        ax.text(i + width/2, f + 0.2, f'{f:.2f}', ha='center', va='bottom', fontsize=9)

    # Highlight zero variance for hierarchical
    ax.axhline(y=0, color='#2E86AB', linestyle='--', linewidth=2, alpha=0.5, label='Zero Variance')

    # Panel C: Statistical Significance (Levene Test p-values)
    ax = axes[2]
    bars = ax.bar(x, levene_pvals, width*2, color='#F18F01', alpha=0.8)

    ax.set_xlabel('Spawn Frequency (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Levene Test p-value', fontsize=11, fontweight='bold')
    ax.set_title('C. Variance Equality Test', fontsize=12, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(freq_labels)
    ax.set_yscale('log')
    ax.grid(axis='y', alpha=0.3, linestyle='--', which='both')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add significance threshold line (p = 0.05)
    ax.axhline(y=0.05, color='red', linestyle='--', linewidth=2, label='p = 0.05 threshold')
    ax.legend(frameon=True, shadow=True, fontsize=9, loc='upper right')

    # Add value labels with significance stars
    for i, pval in enumerate(levene_pvals):
        stars = '***' if pval < 0.001 else ('**' if pval < 0.01 else ('*' if pval < 0.05 else 'ns'))
        ax.text(i, pval * 1.5, f'p={pval:.4f}\n{stars}', ha='center', va='bottom',
                fontsize=8, fontweight='bold', color='red')

    # Add interpretation box
    fig.text(0.5, -0.02,
             'Key Finding: Hierarchical systems show ZERO variance (SD=0.0) vs. flat systems (SD=3-9)\n' +
             'All variance differences highly significant (p < 0.003)\n' +
             'Interpretation: Hierarchical architecture provides robustness through STABILITY',
             ha='center', fontsize=10, style='italic',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='orange', linewidth=2))

    plt.tight_layout()
    return fig

def main():
    """Generate and save figure."""
    print("=" * 80)
    print("GENERATING C189 HIERARCHICAL STABILITY FIGURE")
    print("=" * 80)
    print()

    # Load data
    print(f"Loading data from: {DATA_PATH}")
    data = load_c189_data()

    # Create figure
    print("Creating publication figure...")
    fig = create_figure(data)

    # Save
    print(f"Saving to: {OUTPUT_PATH}")
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight', facecolor='white')
    print()

    # Report statistics
    print("SUMMARY STATISTICS:")
    print("-" * 80)
    print("Hierarchical vs. Flat Comparison:")
    print()

    for freq in ['0.5', '1.0', '1.5', '2.0']:
        freq_data = data['test_results_by_frequency'][freq]
        print(f"  f = {freq}%:")
        print(f"    Hierarchical: μ = {freq_data['hierarchical_mean']:.1f}, SD = {freq_data['hierarchical_std']:.2f}")
        print(f"    Flat:         μ = {freq_data['flat_mean']:.1f}, SD = {freq_data['flat_std']:.2f}")
        print(f"    Variance difference: p = {freq_data['levene_p_value']:.6f} {'***' if freq_data['levene_p_value'] < 0.001 else '**'}")
        print()

    print()
    print("KEY FINDING:")
    print("  Hierarchical systems exhibit PERFECT STABILITY (SD = 0.0) across all frequencies")
    print("  Flat systems show HIGH VARIANCE (SD = 3.2 to 8.6)")
    print("  All variance differences HIGHLY SIGNIFICANT (p < 0.003)")
    print()
    print("INTERPRETATION:")
    print("  Hierarchical architecture provides robustness through STABILITY, not just mean improvement")
    print("=" * 80)
    print()
    print(f"✅ Figure saved: {OUTPUT_PATH}")
    print(f"   Resolution: 300 DPI (publication quality)")
    print(f"   Size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    print()

if __name__ == "__main__":
    main()
