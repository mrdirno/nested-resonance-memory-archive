#!/usr/bin/env python3
"""
Generate Complete Publication Figure Set
For Bistable Dynamics Manuscript

Creates publication-ready figures matching manuscript figure captions:
- Figure 1: Discovery and Precision Mapping
- Figure 2: Multi-Threshold Validation
- Figure 3: Complete Phase Diagram
- Figure 4: Composition Event Rate Validation

All figures: 300 DPI, publication standards
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Publication standards
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

# Color scheme
COLOR_BASIN_A = '#2E86AB'  # Blue - resonance zone
COLOR_BASIN_B = '#EE6C4D'  # Orange - dead zone
COLOR_CRITICAL = '#A23B72'  # Purple - critical line
COLOR_DATA = '#2E86AB'     # Blue - data points
COLOR_FIT = '#A23B72'      # Purple - regression fit


def create_figure1_discovery_precision():
    """
    Figure 1: Discovery and Precision Mapping
    (A) C168 Discovery - Basin A % vs frequency (1.0-3.0%)
    (B) C169 Precision - High-resolution bifurcation (0.1% steps)
    """
    # Load data
    c168_file = Path(__file__).parent / 'results' / 'cycle168_bistability_discovery.json'
    c169_file = Path(__file__).parent / 'results' / 'cycle169_critical_transition_mapping.json'

    with open(c168_file, 'r') as f:
        c168_data = json.load(f)
    with open(c169_file, 'r') as f:
        c169_data = json.load(f)

    # Extract C168 data
    c168_freqs = c168_data['metadata']['frequencies']
    c168_basin_summary = c168_data['basin_summary']
    c168_basin_a_pct = [c168_basin_summary[str(f)]['basin_a_pct'] for f in c168_freqs]

    # Extract C169 data
    c169_freqs = c169_data['metadata']['frequencies']
    c169_basin_summary = c169_data['basin_summary']
    c169_basin_a_pct = [c169_basin_summary[str(f)]['basin_a_pct'] for f in c169_freqs]
    c169_critical = c169_data['transition_analysis']['critical_frequency']

    # Create figure with two panels
    fig = plt.figure(figsize=(14, 5))
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3)

    # Panel A: C168 Discovery
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(c168_freqs, c168_basin_a_pct, 'o-', linewidth=2.5,
             markersize=10, color=COLOR_DATA, label='Observed', zorder=3)
    ax1.axhspan(0, 50, alpha=0.15, color=COLOR_BASIN_B, label='Dead Zone (Basin B)')
    ax1.axhspan(50, 100, alpha=0.15, color=COLOR_BASIN_A, label='Resonance Zone (Basin A)')
    ax1.set_xlabel('Spawn Frequency (%)', fontweight='bold')
    ax1.set_ylabel('Basin A Percentage (%)', fontweight='bold')
    ax1.set_title('(A) C168: Initial Discovery', fontweight='bold', loc='left')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', framealpha=0.95)
    ax1.set_ylim(-5, 105)
    ax1.set_xlim(0.8, 3.2)

    # Add annotation for transition
    ax1.annotate('Sharp transition\n2.0% → 2.5%',
                xy=(2.25, 50), xytext=(1.3, 70),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'),
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Panel B: C169 Precision
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(c169_freqs, c169_basin_a_pct, 'o-', linewidth=2.5,
             markersize=8, color=COLOR_DATA, label='Observed', zorder=3)
    ax2.axvline(c169_critical, color=COLOR_CRITICAL, linestyle='--',
               linewidth=2.5, label=f'Critical = {c169_critical:.2f}%', zorder=2)
    ax2.axhspan(0, 50, alpha=0.15, color=COLOR_BASIN_B)
    ax2.axhspan(50, 100, alpha=0.15, color=COLOR_BASIN_A)
    ax2.set_xlabel('Spawn Frequency (%)', fontweight='bold')
    ax2.set_ylabel('Basin A Percentage (%)', fontweight='bold')
    ax2.set_title('(B) C169: Precision Mapping', fontweight='bold', loc='left')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper left', framealpha=0.95)
    ax2.set_ylim(-5, 105)
    ax2.set_xlim(1.9, 3.1)

    # Add annotation for first-order transition
    ax2.annotate('First-order transition:\n0% → 100% in 0.1%',
                xy=(2.55, 50), xytext=(2.2, 75),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'),
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Save
    output_path = Path(__file__).parent / 'visualizations' / 'Figure1_Discovery_Precision.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Figure 1 created: {output_path}")
    return output_path


def create_figure2_multithreshold_validation():
    """
    Figure 2: Multi-Threshold Validation
    (A) Threshold-specific bifurcation diagrams (5 thresholds)
    (B) Linear regression: critical frequency vs threshold
    """
    # Load C170 data
    c170_file = Path(__file__).parent / 'results' / 'cycle170_basin_threshold_sensitivity.json'

    with open(c170_file, 'r') as f:
        c170_data = json.load(f)

    # Extract threshold analyses
    threshold_analyses = c170_data['threshold_analyses']
    thresholds = sorted([float(t) for t in threshold_analyses.keys()])

    # Linear regression data
    lr = c170_data['linear_regression']
    slope = lr['slope']
    intercept = lr['intercept']
    r_squared = lr['r_squared']

    # Create figure with two panels
    fig = plt.figure(figsize=(14, 5.5))
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3)

    # Panel A: Threshold-specific bifurcations
    ax1 = fig.add_subplot(gs[0, 0])

    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(thresholds)))

    for i, thresh in enumerate(thresholds):
        thresh_data = threshold_analyses[str(thresh)]
        freqs = thresh_data['frequencies']
        basin_a_pcts = thresh_data['basin_a_percentages']
        critical_freq = thresh_data['critical_frequency']

        # Plot bifurcation curve
        ax1.plot(freqs, basin_a_pcts, 'o-', linewidth=2, markersize=6,
                color=colors[i], label=f'Threshold = {thresh}', alpha=0.8)

        # Mark critical frequency
        if critical_freq is not None:
            ax1.axvline(critical_freq, color=colors[i], linestyle='--',
                       linewidth=1.5, alpha=0.5)

    ax1.set_xlabel('Spawn Frequency (%)', fontweight='bold')
    ax1.set_ylabel('Basin A Percentage (%)', fontweight='bold')
    ax1.set_title('(A) Threshold-Dependent Bifurcations', fontweight='bold', loc='left')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left', framealpha=0.95, fontsize=8)
    ax1.set_ylim(-5, 105)

    # Panel B: Linear regression
    ax2 = fig.add_subplot(gs[0, 1])

    # Extract critical frequencies
    critical_freqs = []
    valid_thresholds = []
    for t in thresholds:
        cf = threshold_analyses[str(t)]['critical_frequency']
        if cf is not None:
            critical_freqs.append(cf)
            valid_thresholds.append(t)

    # Data points
    ax2.scatter(valid_thresholds, critical_freqs, s=120, color=COLOR_DATA,
               edgecolors='black', linewidths=2, zorder=3,
               label='Measured Critical Frequencies')

    # Linear fit
    x_fit = np.linspace(min(valid_thresholds) - 0.3, max(valid_thresholds) + 0.3, 100)
    y_fit = slope * x_fit + intercept
    ax2.plot(x_fit, y_fit, '--', linewidth=3, color=COLOR_FIT,
            label=f'Linear Fit: y = {slope:.3f}x + {intercept:.3f}', zorder=2)

    # Ideal 1:1 line
    ax2.plot(x_fit, x_fit, ':', linewidth=2, color='gray',
            alpha=0.6, label='Ideal 1:1 Line', zorder=1)

    ax2.set_xlabel('Basin Threshold (events/window)', fontweight='bold')
    ax2.set_ylabel('Critical Frequency (%)', fontweight='bold')
    ax2.set_title('(B) Linear Relationship Validation', fontweight='bold', loc='left')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper left', framealpha=0.95, fontsize=9)
    ax2.set_aspect('equal')

    # R² annotation
    ax2.text(0.05, 0.95, f'R² = {r_squared:.4f}\nSlope = {slope:.4f}\nIntercept = {intercept:.4f}',
            transform=ax2.transAxes, verticalalignment='top',
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))

    # Save
    output_path = Path(__file__).parent / 'visualizations' / 'Figure2_Multithreshold_Validation.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Figure 2 created: {output_path}")
    return output_path


def create_figure3_phase_diagram():
    """
    Figure 3: Complete Phase Diagram
    2D parameter space: frequency × threshold
    Critical line separating dead zone from resonance zone
    """
    # Use C170 validated parameters
    slope = 0.98
    intercept = 0.04

    fig, ax = plt.subplots(figsize=(10, 8))

    # Create meshgrid
    freq = np.linspace(0.5, 5.0, 300)
    thresh = np.linspace(0.8, 4.5, 300)
    F, T = np.meshgrid(freq, thresh)

    # Calculate critical line: freq = slope * threshold + intercept
    critical_freq = slope * T + intercept

    # Basin classification (Basin A where freq > critical)
    basin = np.where(F > critical_freq, 1, 0)

    # Plot phase regions with smooth shading
    im = ax.contourf(F, T, basin, levels=[0, 0.5, 1],
                    colors=[COLOR_BASIN_B, COLOR_BASIN_A], alpha=0.35)

    # Critical line
    critical_line_freq = slope * thresh + intercept
    ax.plot(critical_line_freq, thresh, 'k-', linewidth=4,
           label=f'Critical Line: f = {slope:.2f}t + {intercept:.2f}', zorder=3)

    # Add experimental validation points from C170
    c170_file = Path(__file__).parent / 'results' / 'cycle170_basin_threshold_sensitivity.json'
    with open(c170_file, 'r') as f:
        c170_data = json.load(f)

    threshold_analyses = c170_data['threshold_analyses']
    thresholds = sorted([float(t) for t in threshold_analyses.keys()])
    critical_freqs = []
    valid_thresholds = []
    for t in thresholds:
        cf = threshold_analyses[str(t)]['critical_frequency']
        if cf is not None:
            critical_freqs.append(cf)
            valid_thresholds.append(t)

    # Plot validation points on critical line
    ax.scatter(critical_freqs, valid_thresholds, s=150, color='yellow',
              edgecolors='black', linewidths=2.5, zorder=4,
              label='C170 Validated Points', marker='*')

    # Region labels
    ax.text(1.5, 3.5, 'Dead Zone\n(Basin B)', fontsize=16, fontweight='bold',
           ha='center', va='center', color='white',
           bbox=dict(boxstyle='round', facecolor=COLOR_BASIN_B, alpha=0.8, edgecolor='black', linewidth=2))

    ax.text(4.0, 2.0, 'Resonance Zone\n(Basin A)', fontsize=16, fontweight='bold',
           ha='center', va='center', color='white',
           bbox=dict(boxstyle='round', facecolor=COLOR_BASIN_A, alpha=0.8, edgecolor='black', linewidth=2))

    ax.set_xlabel('Spawn Frequency (%)', fontweight='bold', fontsize=14)
    ax.set_ylabel('Basin Threshold (events/window)', fontweight='bold', fontsize=14)
    ax.set_title('Complete Bistable Phase Diagram (C168-C170 Validated)',
                fontweight='bold', fontsize=15)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=1.5)
    ax.legend(loc='upper left', framealpha=0.95, fontsize=11)
    ax.set_xlim(0.5, 5.0)
    ax.set_ylim(0.8, 4.5)

    # Save
    output_path = Path(__file__).parent / 'visualizations' / 'Figure3_Phase_Diagram.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Figure 3 created: {output_path}")
    return output_path


def create_figure4_composition_rate_validation():
    """
    Figure 4: Composition Event Rate Validation
    Shows composition events ≈ spawn frequency (1:1 relationship)
    Validates mechanistic hypothesis
    """
    # Load C168-C170 data to extract composition event rates
    c168_file = Path(__file__).parent / 'results' / 'cycle168_bistability_discovery.json'

    with open(c168_file, 'r') as f:
        c168_data = json.load(f)

    # Extract frequencies and composition event rates
    frequencies = c168_data['metadata']['frequencies']
    basin_summary = c168_data['basin_summary']

    avg_composition_events = []
    composition_stds = []

    for f in frequencies:
        trials_data = c168_data['trials'][str(f)]
        comp_events = [trial['avg_composition_events'] for trial in trials_data]
        avg_composition_events.append(np.mean(comp_events))
        composition_stds.append(np.std(comp_events))

    fig, ax = plt.subplots(figsize=(10, 7))

    # Data points with error bars
    ax.errorbar(frequencies, avg_composition_events, yerr=composition_stds,
               fmt='o', markersize=12, color=COLOR_DATA, ecolor='gray',
               elinewidth=2, capsize=5, capthick=2,
               label='Measured Composition Events', zorder=3)

    # Ideal 1:1 line
    x_line = np.array([min(frequencies) - 0.2, max(frequencies) + 0.2])
    ax.plot(x_line, x_line, '--', linewidth=3, color=COLOR_FIT,
           label='Expected: Events = Frequency', zorder=2)

    # Shaded region around 1:1 line (±10% tolerance)
    ax.fill_between(x_line, 0.9 * x_line, 1.1 * x_line,
                    alpha=0.15, color=COLOR_FIT, zorder=1,
                    label='±10% Tolerance')

    ax.set_xlabel('Spawn Frequency (%)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Avg Composition Events (per 100 cycles)', fontweight='bold', fontsize=13)
    ax.set_title('Composition Event Rate ≈ Spawn Frequency', fontweight='bold', fontsize=15)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', framealpha=0.95, fontsize=11)
    ax.set_aspect('equal')

    # Set axis limits to show 1:1 relationship clearly
    max_val = max(max(frequencies), max(avg_composition_events)) + 0.5
    min_val = max(0, min(min(frequencies), min(avg_composition_events)) - 0.5)
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)

    # Add annotation
    ax.text(0.05, 0.95,
           'Mechanistic Validation:\nComposition Rate ≈ Spawn Rate\n(Controls Basin Selection)',
           transform=ax.transAxes, verticalalignment='top',
           fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))

    # Save
    output_path = Path(__file__).parent / 'visualizations' / 'Figure4_Composition_Rate_Validation.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Figure 4 created: {output_path}")
    return output_path


if __name__ == '__main__':
    """Generate all publication figures."""

    print("=" * 80)
    print("GENERATING PUBLICATION FIGURE SET")
    print("=" * 80)
    print()

    # Create output directory
    viz_dir = Path(__file__).parent / 'visualizations'
    viz_dir.mkdir(exist_ok=True)

    try:
        # Generate all figures
        print("Creating Figure 1: Discovery and Precision Mapping...")
        fig1 = create_figure1_discovery_precision()
        print()

        print("Creating Figure 2: Multi-Threshold Validation...")
        fig2 = create_figure2_multithreshold_validation()
        print()

        print("Creating Figure 3: Complete Phase Diagram...")
        fig3 = create_figure3_phase_diagram()
        print()

        print("Creating Figure 4: Composition Rate Validation...")
        fig4 = create_figure4_composition_rate_validation()
        print()

        print("=" * 80)
        print("PUBLICATION FIGURE SET COMPLETE")
        print("=" * 80)
        print()
        print("Generated figures:")
        print(f"  - Figure 1: {fig1}")
        print(f"  - Figure 2: {fig2}")
        print(f"  - Figure 3: {fig3}")
        print(f"  - Figure 4: {fig4}")
        print()
        print("All figures ready for manuscript submission.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
