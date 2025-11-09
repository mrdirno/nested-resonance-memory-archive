#!/usr/bin/env python3
"""
C186 Edge Case Visualization

Creates publication-quality figure comparing V7 and V8 edge case failure patterns
with CPU-based health monitoring annotations.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2 Sonnet 4.5)
Date: 2025-11-08
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Paths
FIGURES_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# V7 Runtime Data (f_migrate=0.00% edge case)
V7_TIMES = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 85])  # minutes
V7_CPU = np.array([100, 28, 25, 22, 20, 18, 19, 21, 20, 18])  # percent

# V8 Runtime Data (n_pop=1 edge case)
V8_TIMES = np.array([0, 2, 7, 12, 23, 29, 33, 38, 41, 52, 71, 73, 76, 78, 80])  # minutes
V8_CPU = np.array([100, 99.4, 99.0, 88.2, 82.0, 47.8, 86.8, 83.4, 83.0, 79.6, 18.6, 21.7, 18.1, 21.8, 15.2])  # percent

# Healthy baseline (typical working experiment)
HEALTHY_TIMES = np.array([0, 10, 20, 30])
HEALTHY_CPU = np.array([100, 99, 99, 98])


def create_edge_case_comparison():
    """Generate edge case CPU pattern comparison figure."""

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=False)

    # V7 Edge Case (f_migrate=0.00%)
    ax1.plot(V7_TIMES, V7_CPU, 'o-', color='#C1121F', linewidth=2.5,
             markersize=8, label='V7: f_migrate=0.00%', zorder=3)

    # Health zones
    ax1.axhspan(79, 100, alpha=0.15, color='#2A9D8F', label='Healthy Zone (79-99% CPU)')
    ax1.axhspan(15, 30, alpha=0.15, color='#E76F51', label='Stuck Zone (15-30% CPU)')

    # Annotations
    ax1.axhline(50, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax1.text(45, 95, 'Stuck from start', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax1.set_ylabel('CPU Usage (%)', fontsize=12, fontweight='bold')
    ax1.set_title('C186 V7: f_migrate=0.00% Edge Case\nInfinite Loop / Stuck State Pattern',
                  fontsize=13, fontweight='bold', pad=15)
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 105)

    # V8 Edge Case (n_pop=1)
    ax2.plot(V8_TIMES, V8_CPU, 'o-', color='#0077B6', linewidth=2.5,
             markersize=8, label='V8: n_pop=1', zorder=3)

    # Health zones
    ax2.axhspan(79, 100, alpha=0.15, color='#2A9D8F', label='Healthy Zone (79-99% CPU)')
    ax2.axhspan(15, 30, alpha=0.15, color='#E76F51', label='Stuck Zone (15-30% CPU)')

    # Phase transitions
    ax2.axvline(52, color='#F4A261', linestyle=':', linewidth=2, alpha=0.7,
                label='Transition Point (52 min)')

    # Annotations
    ax2.axhline(50, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax2.text(20, 95, 'Working Phase', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    ax2.text(65, 25, 'Stuck Phase', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

    ax2.set_xlabel('Runtime (minutes)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('CPU Usage (%)', fontsize=12, fontweight='bold')
    ax2.set_title('C186 V8: n_pop=1 Edge Case\nTransition from Working to Stuck State',
                  fontsize=13, fontweight='bold', pad=15)
    ax2.legend(fontsize=10, loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 105)

    plt.tight_layout()

    # Save
    output_path = FIGURES_DIR / "c186_edge_case_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_hierarchical_advantage_visualization():
    """Generate hierarchical advantage α quantification figure."""

    fig, ax = plt.subplots(figsize=(10, 8))

    # Single-scale vs Hierarchical comparison
    systems = ['Single-Scale\nSystem', 'Hierarchical\nSystem\n(10 populations)']
    critical_freqs = [4.0, 0.0066]  # percent
    colors = ['#E76F51', '#2A9D8F']

    bars = ax.bar(systems, critical_freqs, color=colors, alpha=0.8, edgecolor='black', linewidth=2)

    # Add value labels on bars
    for i, (bar, freq) in enumerate(zip(bars, critical_freqs)):
        height = bar.get_height()
        if i == 0:
            label_text = f'{freq:.1f}%'
            y_pos = height + 0.15
        else:
            label_text = f'{freq:.4f}%\n(extrapolated)'
            y_pos = height + 0.15
        ax.text(bar.get_x() + bar.get_width()/2., y_pos, label_text,
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Add α annotation
    ax.annotate('', xy=(0.5, 3.5), xytext=(1.5, 3.5),
                arrowprops=dict(arrowstyle='<->', lw=2.5, color='#C1121F'))
    ax.text(1.0, 3.8, r'$\alpha = 607\times$' + '\n(600-fold efficiency gain)',
            ha='center', va='bottom', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.9, edgecolor='black', linewidth=2))

    # Efficiency arrow
    ax.annotate('MORE EFFICIENT →', xy=(1.0, -0.4), xytext=(0.0, -0.4),
                fontsize=11, fontweight='bold', color='#2A9D8F',
                arrowprops=dict(arrowstyle='->', lw=2, color='#2A9D8F'))

    ax.set_ylabel('Critical Spawn Frequency (%)', fontsize=13, fontweight='bold')
    ax.set_title('Hierarchical Advantage in Nested Resonance Memory\n' +
                 r'$\alpha = f_{crit}^{single} / f_{crit}^{hier} = 4.0\% / 0.0066\% = 607\times$',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(-0.5, 4.5)
    ax.grid(True, alpha=0.3, axis='y')

    # Add interpretation box
    textstr = 'Hierarchical systems sustain populations\nwith spawn frequencies 600× lower\nthan single-scale systems.\n\nMechanism: Compartmentalization\nenables risk distribution and\nmigration-based rescue.'
    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)

    plt.tight_layout()

    # Save
    output_path = FIGURES_DIR / "c186_hierarchical_advantage_alpha.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def main():
    """Execute figure generation."""
    print("="*80)
    print("C186 EDGE CASE & HIERARCHICAL ADVANTAGE VISUALIZATION")
    print("="*80)
    print()

    print("Generating edge case comparison figure...")
    create_edge_case_comparison()
    print()

    print("Generating hierarchical advantage α visualization...")
    create_hierarchical_advantage_visualization()
    print()

    print("="*80)
    print("VISUALIZATION COMPLETE")
    print("="*80)
    print("Generated:")
    print("  1. c186_edge_case_comparison.png (300 DPI)")
    print("  2. c186_hierarchical_advantage_alpha.png (300 DPI)")
    print()


if __name__ == "__main__":
    main()
