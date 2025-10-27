#!/usr/bin/env python3
"""
Cycle 177 Hypothesis 1 (Energy Pooling) - Figure Generation

Generates publication-quality figures for C177 H1 energy pooling experiment
if results show significant effects (confirmed or strongly confirmed outcomes).

Figures generated:
1. Population trajectories (BASELINE vs POOLING)
2. Birth/death rate comparison
3. Death-birth ratio improvement

Author: Claude (DUALITY-ZERO-V2)
Principal Investigator: Aldrin Payopay
Date: 2025-10-26 (Cycle 227)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List


# Publication settings
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 1.0,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.5
})


def load_results(results_file: str) -> Dict:
    """Load C177 H1 experimental results JSON."""
    with open(results_file, 'r') as f:
        return json.load(f)


def generate_figure_population_trajectories(results: Dict, output_dir: Path):
    """
    Generate Figure: Population Trajectories (BASELINE vs POOLING)

    Shows time series of population for both conditions, demonstrating
    whether energy pooling sustains higher agent counts over time.
    """
    # Extract population time series
    baseline_results = [r for r in results['experiments'] if r['condition'] == 'BASELINE']
    pooling_results = [r for r in results['experiments'] if r['condition'] == 'POOLING']

    # Average population trajectories across seeds
    # Note: This requires time series data in results JSON
    # If not available, fall back to mean ± stderr

    fig, ax = plt.subplots(figsize=(8, 5))

    # Calculate mean populations
    baseline_mean = np.mean([r['mean_population'] for r in baseline_results])
    pooling_mean = np.mean([r['mean_population'] for r in pooling_results])

    # Bar plot comparison
    conditions = ['BASELINE\n(No Pooling)', 'POOLING\n(Cooperative\nEnergy Sharing)']
    means = [baseline_mean, pooling_mean]
    colors = ['#d62728', '#2ca02c']  # Red for baseline, green for pooling

    bars = ax.bar(conditions, means, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add error bars if std available
    baseline_std = np.std([r['mean_population'] for r in baseline_results], ddof=1)
    pooling_std = np.std([r['mean_population'] for r in pooling_results], ddof=1)
    ax.errorbar([0, 1], means, yerr=[baseline_std, pooling_std],
                fmt='none', ecolor='black', capsize=5, capthick=1.5)

    # Add value labels on bars
    for i, (bar, mean) in enumerate(zip(bars, means)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                f'{mean:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax.set_ylabel('Mean Population (agents)', fontweight='bold')
    ax.set_title('Energy Pooling Effect on Sustained Population\n(C177 H1, n=10 per condition, 3,000 cycles)',
                 fontweight='bold', pad=15)
    ax.set_ylim(0, max(means) * 1.3)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Improvement annotation
    if baseline_mean > 0:
        improvement = ((pooling_mean - baseline_mean) / baseline_mean) * 100
        ax.annotate(f'{"+" if improvement > 0 else ""}{improvement:.1f}%',
                    xy=(0.5, max(means) * 1.15), xycoords='data',
                    fontsize=12, fontweight='bold',
                    ha='center', color='green' if improvement > 0 else 'red')

    plt.tight_layout()
    output_file = output_dir / "figure_c177_h1_population_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Generated: {output_file}")


def generate_figure_birth_death_rates(results: Dict, output_dir: Path):
    """
    Generate Figure: Birth and Death Rate Comparison

    Bar plot comparing birth rates and death rates between BASELINE and POOLING
    conditions, showing whether pooling increases birth rate to match death rate.
    """
    baseline_results = [r for r in results['experiments'] if r['condition'] == 'BASELINE']
    pooling_results = [r for r in results['experiments'] if r['condition'] == 'POOLING']

    # Calculate rates
    baseline_birth_rate = np.mean([r['spawn_events'] / 3000 for r in baseline_results])
    pooling_birth_rate = np.mean([r['spawn_events'] / 3000 for r in pooling_results])
    baseline_death_rate = np.mean([r['composition_events'] / 3000 for r in baseline_results])
    pooling_death_rate = np.mean([r['composition_events'] / 3000 for r in pooling_results])

    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(2)
    width = 0.35

    bars1 = ax.bar(x - width/2, [baseline_birth_rate, pooling_birth_rate], width,
                   label='Birth Rate', color='#1f77b4', alpha=0.8, edgecolor='black', linewidth=1.0)
    bars2 = ax.bar(x + width/2, [baseline_death_rate, pooling_death_rate], width,
                   label='Death Rate', color='#d62728', alpha=0.8, edgecolor='black', linewidth=1.0)

    ax.set_ylabel('Event Rate (agents/cycle)', fontweight='bold')
    ax.set_title('Birth vs Death Rates: BASELINE vs POOLING\n(C177 H1, n=10 per condition)',
                 fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(['BASELINE\n(No Pooling)', 'POOLING\n(Cooperative Sharing)'])
    ax.legend(loc='upper right', frameon=True, edgecolor='black')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:.4f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    output_file = output_dir / "figure_c177_h1_birth_death_rates.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Generated: {output_file}")


def generate_figure_death_birth_ratio(results: Dict, output_dir: Path):
    """
    Generate Figure: Death-Birth Ratio Improvement

    Shows death/birth ratio for BASELINE vs POOLING, demonstrating
    whether cooperative energy sharing brings ratio closer to 1.0
    (perfect balance).
    """
    baseline_results = [r for r in results['experiments'] if r['condition'] == 'BASELINE']
    pooling_results = [r for r in results['experiments'] if r['condition'] == 'POOLING']

    # Calculate ratios
    baseline_births = [r['spawn_events'] / 3000 for r in baseline_results]
    pooling_births = [r['spawn_events'] / 3000 for r in pooling_results]
    baseline_deaths = [r['composition_events'] / 3000 for r in baseline_results]
    pooling_deaths = [r['composition_events'] / 3000 for r in pooling_results]

    baseline_ratios = [d / b if b > 0 else float('inf') for b, d in zip(baseline_births, baseline_deaths)]
    pooling_ratios = [d / b if b > 0 else float('inf') for b, d in zip(pooling_births, pooling_deaths)]

    baseline_ratio_mean = np.mean([r for r in baseline_ratios if r != float('inf')])
    pooling_ratio_mean = np.mean([r for r in pooling_ratios if r != float('inf')])

    fig, ax = plt.subplots(figsize=(7, 5))

    conditions = ['BASELINE\n(No Pooling)', 'POOLING\n(Cooperative\nSharing)']
    ratios = [baseline_ratio_mean, pooling_ratio_mean]
    colors = ['#d62728', '#ff7f0e']

    bars = ax.bar(conditions, ratios, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add horizontal line at ratio = 1.0 (perfect balance)
    ax.axhline(y=1.0, color='green', linestyle='--', linewidth=2, label='Perfect Balance (1.0)')

    # Value labels
    for bar, ratio in zip(bars, ratios):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                f'{ratio:.2f}×', ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax.set_ylabel('Death Rate / Birth Rate', fontweight='bold')
    ax.set_title('Death-Birth Imbalance: BASELINE vs POOLING\n(C177 H1, n=10 per condition)',
                 fontweight='bold', pad=15)
    ax.set_ylim(0, max(ratios) * 1.2)
    ax.legend(loc='upper right', frameon=True, edgecolor='black')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Improvement note
    improvement = baseline_ratio_mean - pooling_ratio_mean
    improvement_pct = (improvement / baseline_ratio_mean) * 100
    ax.annotate(f'Imbalance reduced by\n{improvement_pct:.1f}%',
                xy=(0.5, max(ratios) * 0.9), xycoords='data',
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7, edgecolor='black'))

    plt.tight_layout()
    output_file = output_dir / "figure_c177_h1_death_birth_ratio.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Generated: {output_file}")


def main():
    """Generate all C177 H1 figures."""
    # Load results
    results_file = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle177_h1_energy_pooling_results.json")

    if not results_file.exists():
        print(f"ERROR: Results file not found: {results_file}")
        print("Experiment may still be running.")
        return

    print("Loading C177 H1 results...")
    results = load_results(results_file)

    # Output directory
    output_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/figures")
    output_dir.mkdir(exist_ok=True)

    print("Generating figures...")

    # Generate all figures
    generate_figure_population_trajectories(results, output_dir)
    generate_figure_birth_death_rates(results, output_dir)
    generate_figure_death_birth_ratio(results, output_dir)

    print("\n" + "="*80)
    print("C177 H1 FIGURE GENERATION COMPLETE")
    print(f"Output directory: {output_dir}")
    print("Generated 3 figures (300 DPI, publication-ready)")
    print("="*80)


if __name__ == "__main__":
    main()
