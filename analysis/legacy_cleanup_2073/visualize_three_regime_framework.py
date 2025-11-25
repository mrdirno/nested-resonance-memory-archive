#!/usr/bin/env python3
"""
Three-Regime Framework Visualization

Purpose: Generate publication-quality figures comparing V6a (homeostasis),
         V6b (growth), and V6c (collapse) energy regimes.

Figures:
1. Three-regime population comparison (bar chart)
2. Energy phase diagram (net energy vs population)
3. Collapse dynamics (time series for V6c)
4. Spawn rate effect across regimes (side-by-side comparison)

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-18
License: GPL-3.0
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Paths
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
FIGURES_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Publication styling
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['figure.dpi'] = 300

def load_regime_results(regime):
    """Load all results for a specific regime (v6a, v6b, or v6c)"""
    results = []

    if regime == 'v6a':
        pattern = "c186_v6a_HIERARCHICAL_0_*.json"
    elif regime == 'v6b':
        pattern = "c186_v6b_HIERARCHICAL_GROWTH_*.json"
    elif regime == 'v6c':
        pattern = "c186_v6c_HIERARCHICAL_COLLAPSE_*.json"
    else:
        raise ValueError(f"Unknown regime: {regime}")

    for json_file in sorted(RESULTS_DIR.glob(pattern)):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                results.append({
                    'f_spawn': data['parameters']['f_spawn'],
                    'seed': data['seed'],
                    'final_population': data['results']['final_population'],
                    'final_energy': data['results']['final_energy'],
                    'runtime_seconds': data['results']['runtime_seconds']
                })
        except Exception as e:
            print(f"Warning: Failed to load {json_file}: {e}")
            continue

    return pd.DataFrame(results)

def plot_three_regime_comparison():
    """Figure 1: Bar chart comparing population across three regimes"""

    # Load data
    v6a_df = load_regime_results('v6a')
    v6b_df = load_regime_results('v6b')
    v6c_df = load_regime_results('v6c')

    # Calculate means
    v6a_mean = v6a_df['final_population'].mean()
    v6b_mean = v6b_df['final_population'].mean()
    v6c_mean = v6c_df['final_population'].mean()

    v6a_std = v6a_df['final_population'].std()
    v6b_std = v6b_df['final_population'].std()
    v6c_std = v6c_df['final_population'].std()

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    regimes = ['V6c\n(Collapse)\nnet=-0.5', 'V6a\n(Homeostasis)\nnet=0.0', 'V6b\n(Growth)\nnet=+0.5']
    means = [v6c_mean, v6a_mean, v6b_mean]
    stds = [v6c_std, v6a_std, v6b_std]
    colors = ['#e74c3c', '#3498db', '#2ecc71']  # Red, blue, green

    bars = ax.bar(regimes, means, yerr=stds, capsize=10, color=colors,
                   edgecolor='black', linewidth=1.5, alpha=0.7)

    # Add value labels on bars
    for i, (bar, mean, std) in enumerate(zip(bars, means, stds)):
        height = bar.get_height()
        if mean > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + std,
                   f'{mean:.0f} ± {std:.0f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width()/2., 100,
                   f'{mean:.0f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('Final Population (agents)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Energy Regime', fontsize=14, fontweight='bold')
    ax.set_title('Three-Regime Framework: Population by Net Energy\n(C186 V6a/V6b/V6c, n=50 per regime)',
                 fontsize=16, fontweight='bold', pad=20)

    # Log scale for better visualization
    ax.set_yscale('log')
    ax.set_ylim(0.1, 50000)

    ax.grid(True, alpha=0.3, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    output_path = FIGURES_DIR / "three_regime_population_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def plot_energy_phase_diagram():
    """Figure 2: Energy phase diagram (net energy vs population)"""

    # Load data
    v6a_df = load_regime_results('v6a')
    v6b_df = load_regime_results('v6b')
    v6c_df = load_regime_results('v6c')

    fig, ax = plt.subplots(figsize=(10, 6))

    # Net energy values
    net_energy = {
        'v6c': -0.5,
        'v6a': 0.0,
        'v6b': 0.5
    }

    # Plot each regime
    regimes_data = [
        ('v6c', v6c_df, '#e74c3c', 'V6c (Collapse)'),
        ('v6a', v6a_df, '#3498db', 'V6a (Homeostasis)'),
        ('v6b', v6b_df, '#2ecc71', 'V6b (Growth)')
    ]

    for regime, df, color, label in regimes_data:
        net_e = net_energy[regime]
        populations = df['final_population'].values

        # Add jitter to x-axis for visibility
        x_values = np.random.normal(net_e, 0.02, len(populations))

        ax.scatter(x_values, populations, alpha=0.6, s=80, color=color,
                  edgecolor='black', linewidth=0.5, label=label)

    # Add regime boundaries
    ax.axvline(0, color='black', linestyle='--', linewidth=2, alpha=0.5, label='Homeostasis boundary')
    ax.axhspan(0, 1, color='#e74c3c', alpha=0.1)
    ax.axhspan(1, 500, color='#3498db', alpha=0.1)
    ax.axhspan(500, 50000, color='#2ecc71', alpha=0.1)

    ax.set_xlabel('Net Energy per Cycle (E_recharge - E_consume)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Final Population (agents)', fontsize=14, fontweight='bold')
    ax.set_title('Energy Phase Diagram: Population vs Net Energy\n(C186 Three-Regime Framework)',
                 fontsize=16, fontweight='bold', pad=20)

    ax.set_yscale('log')
    ax.set_ylim(0.1, 50000)
    ax.set_xlim(-0.7, 0.7)

    ax.legend(loc='upper left', frameon=True, fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    output_path = FIGURES_DIR / "energy_phase_diagram.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def plot_spawn_rate_effect_across_regimes():
    """Figure 3: Spawn rate effect comparison across regimes"""

    # Load data
    v6a_df = load_regime_results('v6a')
    v6b_df = load_regime_results('v6b')
    v6c_df = load_regime_results('v6c')

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    regimes_data = [
        ('V6c (Collapse)\nnet=-0.5', v6c_df, '#e74c3c', axes[0]),
        ('V6a (Homeostasis)\nnet=0.0', v6a_df, '#3498db', axes[1]),
        ('V6b (Growth)\nnet=+0.5', v6b_df, '#2ecc71', axes[2])
    ]

    for title, df, color, ax in regimes_data:
        spawn_rates = sorted(df['f_spawn'].unique())

        means = []
        stds = []
        for rate in spawn_rates:
            subset = df[df['f_spawn'] == rate]
            means.append(subset['final_population'].mean())
            stds.append(subset['final_population'].std())

        x_pos = np.arange(len(spawn_rates))
        ax.bar(x_pos, means, yerr=stds, capsize=5, color=color,
               edgecolor='black', linewidth=1.5, alpha=0.7)

        ax.set_xlabel('Spawn Rate (f_spawn)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Final Population', fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([f'{r:.3f}' for r in spawn_rates], rotation=45, ha='right')

        # Add horizontal line at mean for reference
        overall_mean = df['final_population'].mean()
        ax.axhline(overall_mean, color='black', linestyle='--', linewidth=1, alpha=0.5)

        ax.grid(True, alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.suptitle('Spawn Rate Effect Across Energy Regimes\n(C186 Three-Regime Framework)',
                 fontsize=16, fontweight='bold', y=1.02)

    plt.tight_layout()
    output_path = FIGURES_DIR / "spawn_rate_effect_across_regimes.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def plot_collapse_time_distribution():
    """Figure 4: V6c collapse time distribution"""

    # Load V6c data with database rows (cycles to collapse)
    results = []
    for json_file in sorted(RESULTS_DIR.glob("c186_v6c_HIERARCHICAL_COLLAPSE_*.json")):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                results.append({
                    'f_spawn': data['parameters']['f_spawn'],
                    'cycles_to_collapse': data['results']['database_rows']
                })
        except Exception as e:
            print(f"Warning: Failed to load {json_file}: {e}")
            continue

    df = pd.DataFrame(results)

    if df.empty:
        print("Warning: No V6c collapse data available yet")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    spawn_rates = sorted(df['f_spawn'].unique())
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(spawn_rates)))

    for i, rate in enumerate(spawn_rates):
        subset = df[df['f_spawn'] == rate]['cycles_to_collapse'].values
        ax.hist(subset, bins=20, alpha=0.6, color=colors[i],
               edgecolor='black', linewidth=1, label=f'f_spawn={rate:.3f}')

    ax.set_xlabel('Cycles to Collapse', fontsize=14, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=14, fontweight='bold')
    ax.set_title('V6c Collapse Dynamics: Time to Population Extinction\n(Net-Negative Energy Regime)',
                 fontsize=16, fontweight='bold', pad=20)

    ax.legend(loc='upper right', frameon=True, fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    output_path = FIGURES_DIR / "v6c_collapse_time_distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

def main():
    """Generate all three-regime framework figures"""

    print("\n" + "="*80)
    print("GENERATING THREE-REGIME FRAMEWORK FIGURES")
    print("="*80 + "\n")

    print("Loading experimental data...")

    # Check data availability
    v6a_count = len(list(RESULTS_DIR.glob("c186_v6a_HIERARCHICAL_0_*.json")))
    v6b_count = len(list(RESULTS_DIR.glob("c186_v6b_HIERARCHICAL_GROWTH_*.json")))
    v6c_count = len(list(RESULTS_DIR.glob("c186_v6c_HIERARCHICAL_COLLAPSE_*.json")))

    print(f"V6a (homeostasis): {v6a_count} experiments")
    print(f"V6b (growth): {v6b_count} experiments")
    print(f"V6c (collapse): {v6c_count} experiments")

    if v6c_count < 50:
        print(f"\n⚠️ WARNING: V6c campaign incomplete ({v6c_count}/50)")
        print("Generating figures with available data...\n")

    print("\nGenerating figures...\n")

    # Generate figures
    plot_three_regime_comparison()
    plot_energy_phase_diagram()
    plot_spawn_rate_effect_across_regimes()

    if v6c_count > 0:
        plot_collapse_time_distribution()

    print("\n" + "="*80)
    print(f"All figures saved to: {FIGURES_DIR}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
