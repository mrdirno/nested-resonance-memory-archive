#!/usr/bin/env python3
"""
Generate temporal evolution figures showing phase transition.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Publication-quality settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'


def load_temporal_data(results_path: Path):
    """Load temporal analysis results."""
    json_files = list(results_path.glob("temporal_analysis_*.json"))
    if not json_files:
        raise FileNotFoundError(f"No temporal analysis JSON found in {results_path}")

    # Load most recent
    latest_file = sorted(json_files)[-1]
    with open(latest_file) as f:
        data = json.load(f)

    return data


def figure1_phase_transition_timeline(data, output_path):
    """
    Figure 1: Temporal evolution of resonance rate showing phase transition.
    """
    print("Generating Figure 1: Phase Transition Timeline...")

    windows = data['windows']
    labels = [w['label'] for w in windows]
    resonance_rates = [w['resonance_rate'] * 100 for w in windows]  # Convert to %
    io_ratios = [w['io_bound_ratio'] * 100 for w in windows]

    # Compute window midpoints in hours
    total_duration_h = data['total_duration_seconds'] / 3600
    window_duration_h = data['window_duration_seconds'] / 3600
    time_points = [(i + 0.5) * window_duration_h for i in range(len(windows))]

    # Create figure with dual y-axis
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot resonance rate (left axis)
    color1 = '#e74c3c'  # Red
    ax1.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Resonance Rate (%)', fontsize=12, fontweight='bold', color=color1)
    line1 = ax1.plot(time_points, resonance_rates, 'o-', color=color1,
                     linewidth=3, markersize=10, label='Resonance Rate')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 110)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Add transition annotation
    transition_idx = 3  # Mid-Late window
    transition_time = time_points[transition_idx]
    ax1.axvline(transition_time, color='purple', linestyle='--',
                linewidth=2, alpha=0.5, label=f'Phase Transition (~{transition_time:.0f}h)')

    # Add regime labels
    ax1.text(time_points[1], 105, 'Initialization\nRegime',
             ha='center', va='top', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax1.text(time_points[-1], 105, 'Steady-State\nRegime',
             ha='center', va='top', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

    # Plot I/O-bound ratio (right axis)
    ax2 = ax1.twinx()
    color2 = '#3498db'  # Blue
    ax2.set_ylabel('I/O-Bound Ratio (%)', fontsize=12, fontweight='bold', color=color2)
    line2 = ax2.plot(time_points, io_ratios, 's-', color=color2,
                     linewidth=2.5, markersize=8, alpha=0.7, label='I/O-Bound Ratio')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(80, 100)

    # Combined legend
    lines = line1 + line2
    labels_legend = [l.get_label() for l in lines]
    ax1.legend(lines, labels_legend, loc='center left', fontsize=10)

    ax1.set_title('Temporal Evolution: Phase Transition from Initialization to Steady-State\n(N=88M+ records, 5 windows × 48.7h)',
                  fontsize=13, fontweight='bold', pad=15)

    plt.tight_layout()
    output_file = output_path / "figure4_phase_transition_timeline.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}")


def figure2_stability_comparison(data, output_path):
    """
    Figure 2: Coefficient of variation comparison showing stability differences.
    """
    print("Generating Figure 2: Stability Comparison (CV)...")

    stability = data['stability_metrics']

    # Prepare data
    metrics = ['Resonance\nRate', 'I/O-Bound\nRatio', 'Mean\nCPU']
    cvs = [
        stability['resonance_rate_cv'] * 100,
        stability['io_ratio_cv'] * 100,
        stability['cpu_cv'] * 100
    ]
    colors = ['#e74c3c', '#2ecc71', '#3498db']

    # Create bar chart
    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(metrics, cvs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add value labels
    for bar, cv in zip(bars, cvs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{cv:.1f}%',
               ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add stability threshold line at 10%
    ax.axhline(10, color='red', linestyle='--', linewidth=2,
               label='Stability Threshold (10%)', alpha=0.7)

    # Add annotations
    ax.text(0, cvs[0] + 5, 'High Variability\n(Phase-Dependent)',
            ha='center', fontsize=9, style='italic')
    ax.text(1, cvs[1] + 5, 'Extremely Stable\n(Fundamental)',
            ha='center', fontsize=9, style='italic')
    ax.text(2, cvs[2] + 5, 'Moderately Stable',
            ha='center', fontsize=9, style='italic')

    ax.set_ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
    ax.set_title('Temporal Stability Analysis: CV Distinguishes Fundamental vs Emergent Properties\n(5 windows × 48.7h, 243.6h total)',
                 fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_ylim(0, max(cvs) * 1.3)

    plt.tight_layout()
    output_file = output_path / "figure5_stability_comparison_cv.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}")


def figure3_regime_comparison(data, output_path):
    """
    Figure 3: Direct comparison of initialization vs steady-state regimes.
    """
    print("Generating Figure 3: Regime Comparison...")

    windows = data['windows']

    # Split into regimes (transition at window 3, index 3)
    init_windows = windows[:3]  # Early, Early-Mid, Mid
    steady_windows = windows[3:]  # Mid-Late, Late

    # Compute regime statistics
    init_resonance = [w['resonance_rate'] * 100 for w in init_windows]
    steady_resonance = [w['resonance_rate'] * 100 for w in steady_windows]

    init_io = [w['io_bound_ratio'] * 100 for w in init_windows]
    steady_io = [w['io_bound_ratio'] * 100 for w in steady_windows]

    # Create 2-panel figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Panel A: Resonance rate
    positions = [1, 2]
    box_data = [init_resonance, steady_resonance]
    bp1 = ax1.boxplot(box_data, positions=positions, widths=0.5, patch_artist=True,
                      labels=['Initialization\n(0-146h)', 'Steady-State\n(146-244h)'])

    for patch, color in zip(bp1['boxes'], ['#ffcccb', '#c8e6c9']):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Add individual points
    for i, (pos, data_points) in enumerate(zip(positions, box_data)):
        x = np.random.normal(pos, 0.04, size=len(data_points))
        ax1.plot(x, data_points, 'o', alpha=0.6, color='black', markersize=8)

    # Add means
    means = [np.mean(init_resonance), np.mean(steady_resonance)]
    ax1.plot(positions, means, 'D', color='red', markersize=10,
             label=f'Means: {means[0]:.1f}% → {means[1]:.1f}%')

    ax1.set_ylabel('Resonance Rate (%)', fontsize=11, fontweight='bold')
    ax1.set_title('A. Resonance Rate by Regime', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(0, 110)

    # Panel B: I/O-bound ratio
    box_data_io = [init_io, steady_io]
    bp2 = ax2.boxplot(box_data_io, positions=positions, widths=0.5, patch_artist=True,
                      labels=['Initialization\n(0-146h)', 'Steady-State\n(146-244h)'])

    for patch in bp2['boxes']:
        patch.set_facecolor('#bbdefb')
        patch.set_alpha(0.7)

    # Add individual points
    for i, (pos, data_points) in enumerate(zip(positions, box_data_io)):
        x = np.random.normal(pos, 0.04, size=len(data_points))
        ax2.plot(x, data_points, 's', alpha=0.6, color='darkblue', markersize=8)

    # Add means
    means_io = [np.mean(init_io), np.mean(steady_io)]
    ax2.plot(positions, means_io, 'D', color='red', markersize=10,
             label=f'Means: {means_io[0]:.1f}% → {means_io[1]:.1f}%')

    # Add stability annotation
    overall_cv = data['stability_metrics']['io_ratio_cv'] * 100
    ax2.text(1.5, 82, f'Overall CV: {overall_cv:.1f}%\n(Extremely Stable)',
             ha='center', fontsize=9, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    ax2.set_ylabel('I/O-Bound Ratio (%)', fontsize=11, fontweight='bold')
    ax2.set_title('B. I/O-Bound Ratio by Regime (Orthogonal)', fontsize=12, fontweight='bold')
    ax2.legend(loc='lower right', fontsize=9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_ylim(80, 100)

    plt.suptitle('Regime Comparison: Resonance Transitions, I/O-Bound Persists',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_file = output_path / "figure6_regime_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}")


def main():
    """Generate all temporal evolution figures."""
    print("="*80)
    print("GENERATING TEMPORAL EVOLUTION FIGURES")
    print("="*80)

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2")
    results_path = workspace / "analysis" / "temporal_evolution"
    output_path = workspace / "analysis" / "temporal_evolution"
    output_path.mkdir(parents=True, exist_ok=True)

    # Load data
    data = load_temporal_data(results_path)
    print(f"Loaded data: {len(data['windows'])} windows, {data['total_duration_seconds']/3600:.1f}h total")
    print()

    # Generate figures
    figure1_phase_transition_timeline(data, output_path)
    figure2_stability_comparison(data, output_path)
    figure3_regime_comparison(data, output_path)

    print()
    print("="*80)
    print("TEMPORAL FIGURES COMPLETE")
    print("="*80)
    print(f"Output directory: {output_path}")
    print()
    print("Generated figures:")
    print("  4. figure4_phase_transition_timeline.png")
    print("  5. figure5_stability_comparison_cv.png")
    print("  6. figure6_regime_comparison.png")
    print()


if __name__ == "__main__":
    main()
