#!/usr/bin/env python3
"""
Generate Publication Figures for Paper 3 - Factorial Synergy Analysis

Purpose: Create publication-quality figures from factorial experiment results:
  1. Synergy heatmap (6 mechanism pairs)
  2. Effect size comparison (individual vs combined)
  3. Classification pie chart (synergistic/antagonistic/additive)
  4. Population trajectories for key interactions

Requirements:
  - matplotlib, seaborn, numpy
  - Results from all 6 factorial experiments (C255-C260)
  - Output: 300 DPI PNG files for publication

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-26
Cycle: 260 (Paper 3 visualization phase)
License: GPL-3.0
"""

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Figure settings (publication quality)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13

# Paths
RESULTS_DIR = Path(__file__).parent / "results"
FIGURES_DIR = Path(__file__).parent / "figures" / "paper3"

# Experiment metadata
EXPERIMENTS = {
    'H1×H2': {
        'file': 'cycle255_h1h2_mechanism_validation_results.json',
        'mechanisms': ('Energy Pooling', 'Reality Sources'),
        'hypothesis': 'SYNERGISTIC'
    },
    'H1×H4': {
        'file': 'cycle256_h1h4_mechanism_validation_results.json',
        'mechanisms': ('Energy Pooling', 'Spawn Throttling'),
        'hypothesis': 'ANTAGONISTIC'
    },
    'H1×H5': {
        'file': 'cycle257_h1h5_mechanism_validation_results.json',
        'mechanisms': ('Energy Pooling', 'Energy Recovery'),
        'hypothesis': 'SYNERGISTIC'
    },
    'H2×H4': {
        'file': 'cycle258_h2h4_mechanism_validation_results.json',
        'mechanisms': ('Reality Sources', 'Spawn Throttling'),
        'hypothesis': 'ADDITIVE'
    },
    'H2×H5': {
        'file': 'cycle259_h2h5_mechanism_validation_results.json',
        'mechanisms': ('Reality Sources', 'Energy Recovery'),
        'hypothesis': 'SYNERGISTIC'
    },
    'H4×H5': {
        'file': 'cycle260_h4h5_mechanism_validation_results.json',
        'mechanisms': ('Spawn Throttling', 'Energy Recovery'),
        'hypothesis': 'ANTAGONISTIC'
    }
}


def load_all_results() -> Dict:
    """Load all factorial experiment results."""
    results = {}
    for exp_name, metadata in EXPERIMENTS.items():
        file_path = RESULTS_DIR / metadata['file']
        if not file_path.exists():
            print(f"⚠️  Missing: {exp_name} ({file_path.name})")
            continue

        with open(file_path, 'r') as f:
            data = json.load(f)

        results[exp_name] = {
            **metadata,
            'synergy_analysis': data['synergy_analysis'],
            'conditions': data['conditions']
        }

    return results


def figure1_synergy_heatmap(results: Dict, save_path: Path):
    """
    Figure 1: Synergy Heatmap
    6×1 grid showing synergy magnitude for each mechanism pair
    """
    exp_names = list(results.keys())
    synergies = [results[name]['synergy_analysis']['synergy'] for name in exp_names]
    classifications = [results[name]['synergy_analysis']['classification'] for name in exp_names]

    # Color map: green=synergistic, red=antagonistic, gray=additive
    colors = []
    for cls in classifications:
        if cls == 'SYNERGISTIC':
            colors.append('#2ca02c')  # Green
        elif cls == 'ANTAGONISTIC':
            colors.append('#d62728')  # Red
        else:
            colors.append('#7f7f7f')  # Gray

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(exp_names, synergies, color=colors, alpha=0.7, edgecolor='black')
    ax.axvline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.set_xlabel('Synergy (Deviation from Additive Prediction)', fontweight='bold')
    ax.set_ylabel('Mechanism Interaction', fontweight='bold')
    ax.set_title('Paper 3: Factorial Synergy Analysis', fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle=':')

    # Add value labels
    for i, (bar, synergy) in enumerate(zip(bars, synergies)):
        x_pos = synergy + (0.05 if synergy > 0 else -0.05)
        ha = 'left' if synergy > 0 else 'right'
        ax.text(x_pos, i, f'{synergy:.3f}', va='center', ha=ha, fontsize=9, fontweight='bold')

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ca02c', alpha=0.7, edgecolor='black', label='Synergistic'),
        Patch(facecolor='#d62728', alpha=0.7, edgecolor='black', label='Antagonistic'),
        Patch(facecolor='#7f7f7f', alpha=0.7, edgecolor='black', label='Additive')
    ]
    ax.legend(handles=legend_elements, loc='lower right')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Figure 1 saved: {save_path}")


def figure2_effect_sizes(results: Dict, save_path: Path):
    """
    Figure 2: Individual vs Combined Effect Sizes
    Grouped bar chart comparing isolated effects to combined effects
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    exp_names = list(results.keys())
    x = np.arange(len(exp_names))
    width = 0.2

    # Extract data
    off_off = [results[name]['synergy_analysis']['off_off'] for name in exp_names]
    on_off = [results[name]['synergy_analysis']['on_off'] for name in exp_names]
    off_on = [results[name]['synergy_analysis']['off_on'] for name in exp_names]
    on_on = [results[name]['synergy_analysis']['on_on'] for name in exp_names]

    # Plot bars
    ax.bar(x - 1.5*width, off_off, width, label='OFF-OFF (Baseline)', color='#1f77b4', alpha=0.8)
    ax.bar(x - 0.5*width, on_off, width, label='ON-OFF (Mech 1 only)', color='#ff7f0e', alpha=0.8)
    ax.bar(x + 0.5*width, off_on, width, label='OFF-ON (Mech 2 only)', color='#2ca02c', alpha=0.8)
    ax.bar(x + 1.5*width, on_on, width, label='ON-ON (Combined)', color='#d62728', alpha=0.8)

    ax.set_xlabel('Mechanism Interaction', fontweight='bold')
    ax.set_ylabel('Mean Population (3000 cycles)', fontweight='bold')
    ax.set_title('Paper 3: Effect Sizes Across Factorial Conditions', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(exp_names, rotation=45, ha='right')
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle=':')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Figure 2 saved: {save_path}")


def figure3_classification_pie(results: Dict, save_path: Path):
    """
    Figure 3: Classification Distribution
    Pie chart showing proportion of synergistic/antagonistic/additive interactions
    """
    classifications = [results[name]['synergy_analysis']['classification'] for name in results.keys()]

    counts = {
        'SYNERGISTIC': classifications.count('SYNERGISTIC'),
        'ANTAGONISTIC': classifications.count('ANTAGONISTIC'),
        'ADDITIVE': classifications.count('ADDITIVE')
    }

    labels = [f"{k}\n(n={v})" for k, v in counts.items() if v > 0]
    sizes = [v for v in counts.values() if v > 0]
    colors = ['#2ca02c', '#d62728', '#7f7f7f'][:len(sizes)]
    explode = [0.05] * len(sizes)

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        explode=explode,
        startangle=90,
        textprops={'fontsize': 11, 'fontweight': 'bold'}
    )

    ax.set_title('Paper 3: Mechanism Interaction Classification\n(n=6 factorial pairs)',
                 fontweight='bold', fontsize=13)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Figure 3 saved: {save_path}")


def figure4_population_trajectories(results: Dict, save_path: Path):
    """
    Figure 4: Population Trajectories for Key Interactions
    Line plots showing population dynamics for selected experiments
    """
    # Select 3 most interesting experiments (highest/lowest synergy, one additive)
    synergies = [(name, results[name]['synergy_analysis']['synergy']) for name in results.keys()]
    synergies_sorted = sorted(synergies, key=lambda x: x[1])

    selected = [
        synergies_sorted[0][0],   # Most antagonistic
        synergies_sorted[-1][0],  # Most synergistic
        synergies_sorted[len(synergies_sorted)//2][0]  # Middle (likely additive)
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    for i, exp_name in enumerate(selected):
        ax = axes[i]
        exp_data = results[exp_name]

        # Extract population histories for all 4 conditions
        conditions = exp_data['conditions']
        off_off_pop = conditions['OFF-OFF']['population_history']
        on_off_pop = conditions['ON-OFF']['population_history']
        off_on_pop = conditions['OFF-ON']['population_history']
        on_on_pop = conditions['ON-ON']['population_history']

        cycles = np.arange(len(off_off_pop))

        ax.plot(cycles, off_off_pop, label='OFF-OFF', color='#1f77b4', alpha=0.7, linewidth=1.5)
        ax.plot(cycles, on_off_pop, label='ON-OFF', color='#ff7f0e', alpha=0.7, linewidth=1.5)
        ax.plot(cycles, off_on_pop, label='OFF-ON', color='#2ca02c', alpha=0.7, linewidth=1.5)
        ax.plot(cycles, on_on_pop, label='ON-ON', color='#d62728', alpha=0.7, linewidth=2.0)

        synergy = exp_data['synergy_analysis']['synergy']
        classification = exp_data['synergy_analysis']['classification']

        ax.set_xlabel('Cycle', fontweight='bold')
        ax.set_ylabel('Population Size', fontweight='bold')
        ax.set_title(f"{exp_name}\n{classification} (synergy={synergy:.3f})",
                     fontweight='bold', fontsize=11)
        ax.legend(loc='best', fontsize=8, framealpha=0.9)
        ax.grid(alpha=0.3, linestyle=':')
        ax.set_ylim(bottom=0)

    fig.suptitle('Paper 3: Population Trajectories Across Conditions',
                 fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Figure 4 saved: {save_path}")


def main():
    """Generate all Paper 3 figures."""
    print("=" * 70)
    print("PAPER 3: FIGURE GENERATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Create output directory
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Load results
    print("Loading factorial experiment results...")
    results = load_all_results()

    if len(results) < 6:
        print(f"❌ Incomplete results: {len(results)}/6 experiments available")
        print("   Missing experiments will be skipped in figures")
        if len(results) == 0:
            print("   No results found - ensure experiments have completed")
            return 1

    print(f"✅ Loaded {len(results)}/6 experiments")
    print()

    # Generate figures
    print("Generating publication figures...")

    try:
        figure1_synergy_heatmap(results, FIGURES_DIR / "figure1_synergy_heatmap.png")
        figure2_effect_sizes(results, FIGURES_DIR / "figure2_effect_sizes.png")
        figure3_classification_pie(results, FIGURES_DIR / "figure3_classification_distribution.png")
        figure4_population_trajectories(results, FIGURES_DIR / "figure4_population_trajectories.png")
    except Exception as e:
        print(f"❌ Figure generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print()
    print("=" * 70)
    print("FIGURE GENERATION COMPLETE")
    print("=" * 70)
    print(f"Output directory: {FIGURES_DIR}")
    print(f"Figures: 4 × 300 DPI PNG files")
    print()
    print("Next steps:")
    print("  1. Review figures for publication quality")
    print("  2. Integrate into Paper 3 manuscript")
    print("  3. Adjust styling/layout if needed")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
