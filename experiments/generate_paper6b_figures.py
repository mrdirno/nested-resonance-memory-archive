#!/usr/bin/env python3
"""
Generate figures for Paper 6B: Multi-Timescale Phase Autonomy Dynamics

Creates publication-quality figures (300 DPI) for manuscript submission:
1. Exponential decay curve (F-ratio vs. cycles)
2. Three temporal regimes diagram
3. Slope distributions across timescales
4. Critical transition region (200-400 cycles)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10


def load_experiment_data() -> Dict:
    """Load data from all three experiments."""
    base_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")

    data = {
        'cycle493': json.load(open(base_path / "cycle493_phase_autonomy_energy_dependence.json")),
        'cycle494': json.load(open(base_path / "cycle494_temporal_energy_persistence.json")),
        'cycle495': json.load(open(base_path / "cycle495_decay_dynamics_mapping.json"))
    }

    return data


def figure1_decay_curve(data: Dict, output_dir: Path):
    """
    Figure 1: Exponential Decay of Energy-Dependent Phase Autonomy

    F-ratio vs. cycles with exponential fit and critical transition marker.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Extract F-ratios from experiments
    cycles = [200]  # C493
    f_ratios = [data['cycle493']['statistical_test']['f_ratio']]

    # Add C495 timescales
    for timescale in data['cycle495']['timescales']:
        cycles.append(timescale['cycles'])
        f_ratios.append(timescale['f_ratio'])

    # Plot measured data
    ax.scatter(cycles, f_ratios, s=100, c='darkblue', marker='o',
               label='Measured F-ratio', zorder=3, edgecolors='black', linewidths=1)

    # Exponential fit
    tau = data['cycle495']['decay_model']['tau_cycles']
    F_0 = data['cycle495']['decay_model']['F_0']
    t_c = data['cycle495']['decay_model']['t_critical_cycles']

    t_fit = np.linspace(0, 1000, 200)
    F_fit = F_0 * np.exp(-t_fit / tau)

    ax.plot(t_fit, F_fit, 'r--', linewidth=2,
            label=f'Exponential fit: F(t) = {F_0:.2f} exp(-t/{tau:.0f})', zorder=2)

    # Critical transition line
    ax.axvline(t_c, color='green', linestyle=':', linewidth=2,
               label=f'Critical transition (t_c = {t_c:.0f} cycles)', zorder=1)
    ax.axhline(1.0, color='gray', linestyle='--', linewidth=1,
               label='Significance threshold (F = 1.0)', alpha=0.5)

    # Shaded regions for temporal regimes
    ax.axvspan(0, 200, alpha=0.1, color='red', label='Transient regime')
    ax.axvspan(200, 400, alpha=0.1, color='yellow', label='Transition regime')
    ax.axvspan(400, 1000, alpha=0.1, color='blue', label='Asymptotic regime')

    ax.set_xlabel('Cycles (t)', fontsize=12)
    ax.set_ylabel('F-ratio (between-condition variance)', fontsize=12)
    ax.set_title('Exponential Decay of Energy-Dependent Phase Autonomy', fontsize=14, fontweight='bold')

    ax.set_xlim(-50, 1050)
    ax.set_ylim(-0.1, 2.8)

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', framealpha=0.95)

    # Add annotation for decay timescale
    ax.annotate(f'τ = {tau:.0f} cycles\n(63% decay)',
                xy=(tau, F_0 * np.exp(-1)), xytext=(tau + 150, 1.0),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                fontsize=10, color='red', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_dir / 'figure1_decay_curve.png', dpi=300, bbox_inches='tight')
    print(f"✓ Figure 1 saved: {output_dir / 'figure1_decay_curve.png'}")
    plt.close()


def figure2_temporal_regimes(data: Dict, output_dir: Path):
    """
    Figure 2: Three Temporal Regimes of Phase Autonomy Evolution

    Three-panel diagram showing transient, transition, and asymptotic regimes.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Extract slope data
    c493_uniform = [a['autonomy_slope'] for a in data['cycle493']['conditions'][0]['agents']]
    c493_highvar = [a['autonomy_slope'] for a in data['cycle493']['conditions'][1]['agents']]

    c494_uniform = [a['autonomy_slope'] for a in data['cycle494']['conditions'][0]['agents']]
    c494_highvar = [a['autonomy_slope'] for a in data['cycle494']['conditions'][1]['agents']]

    c495_400_uniform = [a['autonomy_slope'] for a in data['cycle495']['timescales'][0]['conditions'][0]['agents']]
    c495_400_highvar = [a['autonomy_slope'] for a in data['cycle495']['timescales'][0]['conditions'][1]['agents']]

    # Panel 1: Transient Regime (200 cycles)
    ax = axes[0]
    x_pos = [1, 2]
    means = [np.mean(c493_uniform), np.mean(c493_highvar)]
    stds = [np.std(c493_uniform), np.std(c493_highvar)]

    bars = ax.bar(x_pos, means, yerr=stds, capsize=5,
                   color=['blue', 'orange'], alpha=0.7, edgecolor='black', linewidth=1.5)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Uniform', 'High-Variance'])
    ax.set_ylabel('Autonomy Slope (×10⁻⁴)', fontsize=11)
    ax.set_title('Transient Regime\n(t = 200 cycles, F = 2.39)', fontsize=12, fontweight='bold')
    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_ylim(-0.0003, 0.00015)
    ax.grid(True, alpha=0.3, axis='y')

    # Add significance marker
    ax.plot([1, 2], [0.00012, 0.00012], 'k-', linewidth=2)
    ax.text(1.5, 0.00013, '**', ha='center', fontsize=14, fontweight='bold')

    # Panel 2: Transition Regime (400 cycles)
    ax = axes[1]
    means = [np.mean(c495_400_uniform), np.mean(c495_400_highvar)]
    stds = [np.std(c495_400_uniform), np.std(c495_400_highvar)]

    bars = ax.bar(x_pos, means, yerr=stds, capsize=5,
                   color=['blue', 'orange'], alpha=0.7, edgecolor='black', linewidth=1.5)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Uniform', 'High-Variance'])
    ax.set_ylabel('Autonomy Slope (×10⁻⁴)', fontsize=11)
    ax.set_title('Transition Regime\n(t = 400 cycles, F = 0.41)', fontsize=12, fontweight='bold')
    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_ylim(-0.0003, 0.00015)
    ax.grid(True, alpha=0.3, axis='y')

    # Add "n.s." marker (not significant)
    ax.text(1.5, 0.00012, 'n.s.', ha='center', fontsize=12, style='italic')

    # Panel 3: Asymptotic Regime (1000 cycles)
    ax = axes[2]
    means = [np.mean(c494_uniform), np.mean(c494_highvar)]
    stds = [np.std(c494_uniform), np.std(c494_highvar)]

    bars = ax.bar(x_pos, means, yerr=stds, capsize=5,
                   color=['blue', 'orange'], alpha=0.7, edgecolor='black', linewidth=1.5)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Uniform', 'High-Variance'])
    ax.set_ylabel('Autonomy Slope (×10⁻⁴)', fontsize=11)
    ax.set_title('Asymptotic Regime\n(t = 1000 cycles, F = 0.12)', fontsize=12, fontweight='bold')
    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_ylim(-0.0003, 0.00015)
    ax.grid(True, alpha=0.3, axis='y')

    # Add "n.s." marker
    ax.text(1.5, 0.00012, 'n.s.', ha='center', fontsize=12, style='italic')

    plt.tight_layout()
    plt.savefig(output_dir / 'figure2_temporal_regimes.png', dpi=300, bbox_inches='tight')
    print(f"✓ Figure 2 saved: {output_dir / 'figure2_temporal_regimes.png'}")
    plt.close()


def figure3_slope_distributions(data: Dict, output_dir: Path):
    """
    Figure 3: Slope Distribution Evolution Across Timescales

    Violin plots showing how uniform vs. high-variance distributions converge.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Collect all slope data
    timescales = [200, 400, 600, 800, 1000]
    uniform_slopes = []
    highvar_slopes = []

    # 200 cycles (C493)
    uniform_slopes.append([a['autonomy_slope'] for a in data['cycle493']['conditions'][0]['agents']])
    highvar_slopes.append([a['autonomy_slope'] for a in data['cycle493']['conditions'][1]['agents']])

    # 400-1000 cycles (C495)
    for timescale in data['cycle495']['timescales']:
        uniform_slopes.append([a['autonomy_slope'] for a in timescale['conditions'][0]['agents']])
        highvar_slopes.append([a['autonomy_slope'] for a in timescale['conditions'][1]['agents']])

    # Prepare data for violin plot
    all_data = []
    positions = []
    colors = []

    for i, t in enumerate(timescales):
        all_data.append(uniform_slopes[i])
        positions.append(i * 2)
        colors.append('blue')

        all_data.append(highvar_slopes[i])
        positions.append(i * 2 + 0.8)
        colors.append('orange')

    # Create violin plot
    parts = ax.violinplot(all_data, positions=positions, widths=0.6,
                          showmeans=True, showmedians=True)

    # Color the violins
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)
        pc.set_edgecolor('black')
        pc.set_linewidth(1.5)

    # Set x-axis labels
    ax.set_xticks([i * 2 + 0.4 for i in range(len(timescales))])
    ax.set_xticklabels([f'{t} cycles' for t in timescales])
    ax.set_xlabel('Timescale', fontsize=12)
    ax.set_ylabel('Autonomy Slope', fontsize=12)
    ax.set_title('Convergence of Slope Distributions Across Timescales', fontsize=14, fontweight='bold')

    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.grid(True, alpha=0.3, axis='y')

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='blue', alpha=0.7, edgecolor='black', label='Uniform'),
                      Patch(facecolor='orange', alpha=0.7, edgecolor='black', label='High-Variance')]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(output_dir / 'figure3_slope_distributions.png', dpi=300, bbox_inches='tight')
    print(f"✓ Figure 3 saved: {output_dir / 'figure3_slope_distributions.png'}")
    plt.close()


def figure4_critical_transition(data: Dict, output_dir: Path):
    """
    Figure 4: Critical Transition Region (200-400 cycles)

    Zoomed view highlighting where F-ratio crosses 1.0 threshold.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Exponential model parameters
    tau = data['cycle495']['decay_model']['tau_cycles']
    F_0 = data['cycle495']['decay_model']['F_0']
    t_c = data['cycle495']['decay_model']['t_critical_cycles']

    # Fine-grained timescale
    t_fine = np.linspace(150, 450, 500)
    F_fine = F_0 * np.exp(-t_fine / tau)

    ax.plot(t_fine, F_fine, 'r-', linewidth=3, label='Exponential model: F(t) = 2.39 exp(-t/454)')

    # Plot measured points in this region
    cycles = [200, 400]
    f_ratios = [data['cycle493']['statistical_test']['f_ratio'],
                data['cycle495']['timescales'][0]['f_ratio']]

    ax.scatter(cycles, f_ratios, s=150, c='darkblue', marker='o',
               label='Measured data', zorder=3, edgecolors='black', linewidths=2)

    # Critical transition
    ax.axvline(t_c, color='green', linestyle='--', linewidth=3,
               label=f'Critical transition (t_c = {t_c:.1f} cycles)')
    ax.axhline(1.0, color='gray', linestyle='--', linewidth=2,
               label='Significance threshold (F = 1.0)', alpha=0.7)

    # Shade regions
    ax.axvspan(150, t_c, alpha=0.15, color='red', label='Significant (F > 1.0)')
    ax.axvspan(t_c, 450, alpha=0.15, color='blue', label='Non-significant (F < 1.0)')

    # Annotate key points
    ax.annotate(f'F = {F_0:.2f}\n(strong)', xy=(200, F_0), xytext=(170, 2.7),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=11, fontweight='bold', color='red',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.annotate(f'F = 1.0\n(threshold)', xy=(t_c, 1.0), xytext=(350, 1.5),
                arrowprops=dict(arrowstyle='->', color='green', lw=2),
                fontsize=11, fontweight='bold', color='green',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.annotate(f'F = 0.41\n(weak)', xy=(400, 0.41), xytext=(380, 0.1),
                arrowprops=dict(arrowstyle='->', color='blue', lw=2),
                fontsize=11, fontweight='bold', color='blue',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax.set_xlabel('Cycles (t)', fontsize=12)
    ax.set_ylabel('F-ratio', fontsize=12)
    ax.set_title('Critical Transition Region: Where Energy Effects Vanish', fontsize=14, fontweight='bold')

    ax.set_xlim(150, 450)
    ax.set_ylim(0, 3.0)

    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', framealpha=0.95, fontsize=9)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure4_critical_transition.png', dpi=300, bbox_inches='tight')
    print(f"✓ Figure 4 saved: {output_dir / 'figure4_critical_transition.png'}")
    plt.close()


def main():
    """Generate all figures for Paper 6B."""
    print("="*70)
    print("GENERATING FIGURES FOR PAPER 6B")
    print("="*70)
    print()

    # Load data
    print("Loading experiment data...")
    data = load_experiment_data()
    print("  ✓ Cycle 493 data loaded")
    print("  ✓ Cycle 494 data loaded")
    print("  ✓ Cycle 495 data loaded")
    print()

    # Create output directory
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/papers/figures/paper6b")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate figures
    print("Generating figures...")
    figure1_decay_curve(data, output_dir)
    figure2_temporal_regimes(data, output_dir)
    figure3_slope_distributions(data, output_dir)
    figure4_critical_transition(data, output_dir)

    print()
    print("="*70)
    print("ALL FIGURES GENERATED SUCCESSFULLY")
    print("="*70)
    print(f"Output directory: {output_dir}")
    print()
    print("Figures:")
    print("  1. figure1_decay_curve.png - Exponential decay with regimes")
    print("  2. figure2_temporal_regimes.png - Three-panel regime comparison")
    print("  3. figure3_slope_distributions.png - Convergence visualization")
    print("  4. figure4_critical_transition.png - Zoomed critical region")
    print()
    print("Ready for manuscript submission!")
    print("="*70)


if __name__ == "__main__":
    main()
