#!/usr/bin/env python3
"""
PAPER 7 PHASE 3: VISUALIZE REGIME BOUNDARIES

Purpose: Create publication figures showing regime boundaries from extreme parameter exploration

Date: 2025-10-27 (Cycle 382)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime
import sys

def load_extreme_results(results_path: Path) -> dict:
    """Load extreme parameter exploration results from JSON."""
    with open(results_path, 'r') as f:
        return json.load(f)


def plot_regime_boundaries(results: dict, output_dir: Path):
    """Create regime boundary plots for all parameters."""

    sweeps = results['sweeps']
    n_sweeps = len(sweeps)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, sweep in enumerate(sweeps):
        ax = axes[i]

        param_name = sweep['param_name']
        param_values = sweep['param_values']
        regimes = sweep['regimes']
        N_mean = sweep['N_mean']

        # Color code by regime
        colors = []
        for regime in regimes:
            if regime == 'sustained':
                colors.append('green')
            elif regime == 'collapsed':
                colors.append('red')
            elif regime == 'intermediate':
                colors.append('orange')
            elif regime == 'oscillatory':
                colors.append('blue')
            elif regime == 'error':
                colors.append('gray')
            else:
                colors.append('black')

        # Plot N_mean vs parameter
        ax.scatter(param_values, N_mean, c=colors, s=50, alpha=0.7)

        # Mark collapse boundary (N=10 threshold)
        ax.axhline(y=10.0, color='k', linestyle='--', alpha=0.5, label='Sustained threshold')
        ax.axhline(y=3.0, color='k', linestyle=':', alpha=0.5, label='Collapsed threshold')

        # Identify boundary regions
        for j in range(len(regimes) - 1):
            if regimes[j] != regimes[j+1] and regimes[j] != 'error' and regimes[j+1] != 'error':
                boundary_param = (param_values[j] + param_values[j+1]) / 2
                ax.axvline(x=boundary_param, color='purple', linestyle='-.', alpha=0.7, linewidth=2)

        ax.set_xlabel(f"{param_name}", fontsize=11)
        ax.set_ylabel("Population (N)", fontsize=11)
        ax.set_title(f"{param_name}: Regime Boundaries", fontsize=12, fontweight='bold')
        ax.grid(alpha=0.3)
        ax.set_yscale('log')

        # Legend (only first subplot)
        if i == 0:
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='green', label='Sustained'),
                Patch(facecolor='red', label='Collapsed'),
                Patch(facecolor='orange', label='Intermediate'),
                Patch(facecolor='blue', label='Oscillatory'),
                Patch(facecolor='gray', label='Error')
            ]
            ax.legend(handles=legend_elements, loc='best', fontsize=9)

    # Remove extra subplot
    if n_sweeps < len(axes):
        fig.delaxes(axes[-1])

    fig.suptitle("V4 Model: Regime Boundaries (Extreme Parameter Exploration)", fontsize=14, fontweight='bold')
    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = output_dir / "figures" / f"paper7_phase3_regime_boundaries_{timestamp}.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Regime boundaries figure saved: {save_path}")
    plt.close()


def analyze_boundaries(results: dict):
    """Analyze and summarize regime boundaries."""
    print("\n" + "=" * 70)
    print("REGIME BOUNDARY ANALYSIS")
    print("=" * 70)
    print()

    sweeps = results['sweeps']

    for sweep in sweeps:
        param_name = sweep['param_name']
        param_values = sweep['param_values']
        regimes = sweep['regimes']
        N_mean = sweep['N_mean']

        print(f"{param_name}:")
        print(f"  Range tested: {param_values[0]:.4f} to {param_values[-1]:.4f}")

        # Count regimes
        n_sustained = regimes.count('sustained')
        n_collapsed = regimes.count('collapsed')
        n_intermediate = regimes.count('intermediate')
        n_error = regimes.count('error')
        n_total = len(regimes)

        print(f"  Sustained: {n_sustained}/{n_total} ({n_sustained/n_total*100:.1f}%)")
        print(f"  Collapsed: {n_collapsed}/{n_total} ({n_collapsed/n_total*100:.1f}%)")
        if n_intermediate > 0:
            print(f"  Intermediate: {n_intermediate}/{n_total} ({n_intermediate/n_total*100:.1f}%)")
        if n_error > 0:
            print(f"  Error: {n_error}/{n_total} ({n_error/n_total*100:.1f}%)")

        # Find boundaries
        boundaries = []
        for i in range(len(regimes) - 1):
            if regimes[i] != regimes[i+1] and regimes[i] != 'error' and regimes[i+1] != 'error':
                boundary = (param_values[i] + param_values[i+1]) / 2
                boundaries.append((regimes[i], regimes[i+1], boundary))

        if boundaries:
            print(f"  Boundaries detected:")
            for regime_from, regime_to, boundary in boundaries:
                print(f"    {regime_from} → {regime_to}: {param_name} ≈ {boundary:.4f}")
        else:
            print(f"  No boundaries detected")

        # Critical values (first sustained, last sustained)
        sustained_indices = [i for i, r in enumerate(regimes) if r == 'sustained']
        if sustained_indices:
            first_sustained = param_values[sustained_indices[0]]
            last_sustained = param_values[sustained_indices[-1]]
            print(f"  Sustained range: {first_sustained:.4f} to {last_sustained:.4f}")

        print()

    print("=" * 70)


def main():
    """Execute boundary visualization and analysis."""
    print("\n" + "=" * 70)
    print("V4 MODEL: REGIME BOUNDARY VISUALIZATION")
    print("=" * 70)
    print()

    # Find most recent extreme parameter results
    data_dir = Path(__file__).parent.parent.parent / "data"
    results_dir = data_dir / "results"

    extreme_results = sorted(results_dir.glob("paper7_phase3_extreme_parameters_*.json"))
    if not extreme_results:
        print("ERROR: No extreme parameter results found")
        return

    latest_results = extreme_results[-1]
    print(f"Loading results: {latest_results.name}")
    print()

    results = load_extreme_results(latest_results)

    # Analyze boundaries
    analyze_boundaries(results)

    # Generate visualization
    print("Generating regime boundary figure...")
    plot_regime_boundaries(results, data_dir)

    print("\n" + "=" * 70)
    print("BOUNDARY VISUALIZATION COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
