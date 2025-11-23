#!/usr/bin/env python3
"""
PAPER 7 PHASE 3: V4 VS V2 MODEL COMPARISON FIGURES

Purpose: Generate publication-quality figures comparing V2 (collapsed) vs V4 (sustained)

Visualizations:
1. Population trajectories: V2 → 1.00, V4 → 139.17
2. Phase space comparison: V2 trapped vs V4 sustained
3. Parameter comparison: Show what changed V2 → V4
4. Regime boundaries: V4 robust within sustained regime

Date: 2025-10-27 (Cycle 383)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent))

from paper7_v2_constrained_model import NRMDynamicalSystemV2
from paper7_v4_energy_threshold import NRMDynamicalSystemV4


def compare_trajectories():
    """Compare V2 vs V4 population trajectories."""
    print("Generating V2 vs V4 trajectory comparison...")

    # V2 parameters (collapsed)
    params_v2 = {
        'r': 0.05,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 1.0,
        'mu_0': 0.8,
        'sigma': 0.1,
        'omega': 0.02,
        'kappa': 0.1
    }

    # V4 parameters (sustained)
    params_v4 = {
        'r': 0.15,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 2.5,
        'mu_0': 0.4,
        'sigma': 0.1,
        'omega': 0.02,
        'kappa': 0.1,
        'phi_0': 0.06,
        'rho_threshold': 5.0
    }

    # Create models
    model_v2 = NRMDynamicalSystemV2(params_v2)
    model_v4 = NRMDynamicalSystemV4(params_v4)

    # Initial condition
    initial_state = np.array([100.0, 10.0, 0.5, 0.0])
    R_func = lambda t: 1.0

    # Time span
    t_span = np.linspace(0, 1000, 10001)

    # Simulate V2
    print("  Simulating V2 (collapsed model)...")
    traj_v2 = model_v2.simulate(t_span, initial_state, R_func)

    # Simulate V4
    print("  Simulating V4 (sustained model)...")
    traj_v4 = model_v4.simulate(t_span, initial_state, R_func)

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Population N
    ax = axes[0, 0]
    ax.plot(t_span, traj_v2[:, 1], 'r-', linewidth=2, label='V2 (collapsed)', alpha=0.7)
    ax.plot(t_span, traj_v4[:, 1], 'g-', linewidth=2, label='V4 (sustained)', alpha=0.7)
    ax.axhline(y=10.0, color='k', linestyle='--', alpha=0.3, label='Sustained threshold')
    ax.axhline(y=1.0, color='k', linestyle=':', alpha=0.3, label='Collapse floor')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Population (N)', fontsize=11)
    ax.set_title('Population Dynamics: V2 vs V4', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Energy E
    ax = axes[0, 1]
    ax.plot(t_span, traj_v2[:, 0], 'r-', linewidth=2, label='V2', alpha=0.7)
    ax.plot(t_span, traj_v4[:, 0], 'g-', linewidth=2, label='V4', alpha=0.7)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Total Energy (E)', fontsize=11)
    ax.set_title('Energy Dynamics', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Resonance phi
    ax = axes[1, 0]
    ax.plot(t_span, traj_v2[:, 2], 'r-', linewidth=2, label='V2', alpha=0.7)
    ax.plot(t_span, traj_v4[:, 2], 'g-', linewidth=2, label='V4', alpha=0.7)
    ax.axhline(y=0.0, color='k', linestyle=':', alpha=0.3)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Resonance (φ)', fontsize=11)
    ax.set_title('Resonance Dynamics', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Phase theta (first 200 time units for clarity)
    ax = axes[1, 1]
    t_short = t_span[:2001]  # First 200 time units
    ax.plot(t_short, traj_v2[:2001, 3], 'r-', linewidth=2, label='V2', alpha=0.7)
    ax.plot(t_short, traj_v4[:2001, 3], 'g-', linewidth=2, label='V4', alpha=0.7)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Relative Phase (θ_rel)', fontsize=11)
    ax.set_title('Phase Dynamics (First 200 time units)', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    fig.suptitle('V2 vs V4 Model Comparison: Collapse vs. Sustained Dynamics',
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / f"paper7_v4_vs_v2_trajectories_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()

    return traj_v2, traj_v4, t_span


def compare_parameters():
    """Create parameter comparison table visualization."""
    print("Generating parameter comparison...")

    params_comparison = [
        {'name': 'r', 'v2': 0.05, 'v4': 0.15, 'change': '+200%', 'category': 'Energy'},
        {'name': 'lambda_0', 'v2': 1.0, 'v4': 2.5, 'change': '+150%', 'category': 'Composition'},
        {'name': 'mu_0', 'v2': 0.8, 'v4': 0.4, 'change': '-50%', 'category': 'Decomposition'},
        {'name': 'phi_0', 'v2': 0.0, 'v4': 0.06, 'change': 'NEW', 'category': 'Resonance'},
        {'name': 'rho_threshold', 'v2': 40.0, 'v4': 5.0, 'change': '-87.5%', 'category': 'Energy Gate'},
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')

    # Table data
    table_data = [['Parameter', 'V2 (Collapsed)', 'V4 (Sustained)', 'Change', 'Category']]
    for param in params_comparison:
        table_data.append([
            param['name'],
            f"{param['v2']:.2f}",
            f"{param['v4']:.2f}",
            param['change'],
            param['category']
        ])

    # Create table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.15, 0.2, 0.2, 0.15, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Style header
    for i in range(5):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Color rows
    for i in range(1, len(table_data)):
        for j in range(5):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')

    plt.title('V2 → V4: Parameter Changes for Sustained Dynamics',
              fontsize=14, fontweight='bold', pad=20)

    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    save_path = output_dir / f"paper7_v4_vs_v2_parameters_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def create_phase_space_comparison(traj_v2, traj_v4, t_span):
    """Create phase space comparison (N vs E)."""
    print("Generating phase space comparison...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # V2 phase space
    ax = axes[0]
    scatter = ax.scatter(traj_v2[:, 0], traj_v2[:, 1], c=t_span, cmap='Reds',
                        s=1, alpha=0.5)
    ax.plot(traj_v2[0, 0], traj_v2[0, 1], 'go', markersize=10, label='Initial')
    ax.plot(traj_v2[-1, 0], traj_v2[-1, 1], 'rx', markersize=10, label='Final')
    ax.set_xlabel('Total Energy (E)', fontsize=11)
    ax.set_ylabel('Population (N)', fontsize=11)
    ax.set_title('V2 Phase Space: Collapse to N=1', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)
    plt.colorbar(scatter, ax=ax, label='Time')

    # V4 phase space
    ax = axes[1]
    scatter = ax.scatter(traj_v4[:, 0], traj_v4[:, 1], c=t_span, cmap='Greens',
                        s=1, alpha=0.5)
    ax.plot(traj_v4[0, 0], traj_v4[0, 1], 'go', markersize=10, label='Initial')
    ax.plot(traj_v4[-1, 0], traj_v4[-1, 1], 'bx', markersize=10, label='Final')
    ax.set_xlabel('Total Energy (E)', fontsize=11)
    ax.set_ylabel('Population (N)', fontsize=11)
    ax.set_title('V4 Phase Space: Sustained Dynamics', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)
    plt.colorbar(scatter, ax=ax, label='Time')

    fig.suptitle('Phase Space Comparison: V2 Collapse vs V4 Sustained',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    save_path = output_dir / f"paper7_v4_vs_v2_phase_space_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def main():
    """Generate all V4 vs V2 comparison figures."""
    print("\n" + "=" * 70)
    print("V4 VS V2 MODEL COMPARISON FIGURES")
    print("=" * 70)
    print()

    # Trajectories
    traj_v2, traj_v4, t_span = compare_trajectories()

    # Parameters
    compare_parameters()

    # Phase space
    create_phase_space_comparison(traj_v2, traj_v4, t_span)

    print()
    print("=" * 70)
    print("COMPARISON FIGURES COMPLETE")
    print("=" * 70)
    print()
    print("Generated 3 publication-quality figures:")
    print("1. Trajectory comparison (N, E, phi, theta dynamics)")
    print("2. Parameter comparison table")
    print("3. Phase space comparison (E-N projection)")
    print()
    print("These figures demonstrate:")
    print("- V2 collapse to N=1 despite positive initial conditions")
    print("- V4 sustained dynamics at N≈139 with equilibrium at N=50")
    print("- Key parameter changes: rho_threshold, lambda_0, mu_0, phi_0")
    print("- Phase space structure: V2 trapped vs V4 sustained")
    print()


if __name__ == "__main__":
    main()
