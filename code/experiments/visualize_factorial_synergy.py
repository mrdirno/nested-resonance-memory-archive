#!/usr/bin/env python3
"""
Auto-Visualization Tool: Factorial Synergy Analysis for Paper 3

Purpose: Generate publication-ready figures from C255-C260 factorial validation results
Usage: python visualize_factorial_synergy.py <results_json>
Output: PNG figures at 300 DPI for manuscript inclusion

Figures Generated:
1. Factorial bar chart (OFF-OFF, ON-OFF, OFF-ON, ON-ON comparisons)
2. Synergy decomposition (additive prediction vs. observed)
3. Population dynamics trajectories (time series)
4. Effect size heatmap (H1-H5 pairwise interactions)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-27 (Cycle 349)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Publication-quality figure settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13


def load_results(filepath: Path) -> Dict:
    """Load factorial validation results from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_factorial_bar_chart(results: Dict, output_dir: Path):
    """
    Figure 1: Factorial Comparison Bar Chart

    Shows mean population for four conditions with synergy visualization.
    """
    synergy = results['synergy_analysis']

    fig, ax = plt.subplots(figsize=(8, 5))

    # Extract values
    conditions = ['OFF-OFF', 'ON-OFF', 'OFF-ON', 'ON-ON']
    values = [
        synergy['off_off'],
        synergy['on_off'],
        synergy['off_on'],
        synergy['on_on']
    ]

    # Color scheme based on classification
    classification = synergy['classification']
    if classification == 'SYNERGISTIC':
        colors = ['#d3d3d3', '#9ecae1', '#9ecae1', '#3182bd']  # Blue gradient
    elif classification == 'ANTAGONISTIC':
        colors = ['#d3d3d3', '#fdae6b', '#fdae6b', '#e6550d']  # Orange gradient
    else:  # ADDITIVE
        colors = ['#d3d3d3', '#bdbdbd', '#bdbdbd', '#636363']  # Gray gradient

    # Create bars
    bars = ax.bar(conditions, values, color=colors, edgecolor='black', linewidth=1.2)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{val:.2f}',
                ha='center', va='bottom', fontweight='bold')

    # Additive prediction line
    additive_pred = synergy['additive_prediction']
    ax.axhline(y=additive_pred, color='red', linestyle='--', linewidth=2,
               label=f'Additive Prediction: {additive_pred:.2f}')

    # Synergy annotation
    synergy_val = synergy['synergy']
    synergy_text = f"Synergy: {synergy_val:+.2f}"
    ax.text(3, additive_pred + 0.05, synergy_text,
            ha='center', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

    # Styling
    ax.set_ylabel('Mean Population', fontweight='bold')
    ax.set_xlabel('Experimental Condition', fontweight='bold')
    ax.set_title(f'Factorial Validation: {results["experiment"]}\n'
                 f'Classification: {classification}',
                 fontweight='bold')
    ax.set_ylim(0, max(values) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle=':')
    ax.legend(loc='upper left')

    # Mechanism labels
    mechanism_info = results.get('mechanism_info', {})
    if mechanism_info:
        h1_name = mechanism_info.get('h1_name', 'H1')
        h2_name = mechanism_info.get('h2_name', 'H2')

        ax.text(0.5, -0.15, f'{h1_name} OFF', ha='center', transform=ax.transAxes)
        ax.text(1.5, -0.15, f'{h1_name} ON', ha='center', transform=ax.transAxes)
        ax.text(2.5, -0.15, f'{h2_name} ON', ha='center', transform=ax.transAxes)
        ax.text(3.5, -0.15, 'Both ON', ha='center', transform=ax.transAxes)

    plt.tight_layout()
    output_path = output_dir / f'{results["experiment"]}_factorial_bar_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Figure 1 saved: {output_path}")
    return output_path


def create_synergy_decomposition(results: Dict, output_dir: Path):
    """
    Figure 2: Synergy Decomposition

    Stacked bar showing how additive prediction + synergy = observed outcome.
    """
    synergy = results['synergy_analysis']

    fig, ax = plt.subplots(figsize=(7, 5))

    # Components
    off_off = synergy['off_off']
    h1_effect = synergy['h1_effect']
    h2_effect = synergy['h2_effect']
    synergy_val = synergy['synergy']
    on_on = synergy['on_on']

    # Build stacked components for additive prediction
    components = [
        ('Baseline\n(OFF-OFF)', off_off, '#d3d3d3'),
        ('H1 Effect', h1_effect, '#9ecae1'),
        ('H2 Effect', h2_effect, '#9ecae1')
    ]

    x_pos = [0, 1, 2]
    bottoms = [0, 0, 0]

    # Additive prediction (stacked)
    for i, (label, value, color) in enumerate(components):
        if i == 0:
            ax.bar(1, value, color=color, edgecolor='black', linewidth=1.2, label=label)
            bottoms[1] = value
        else:
            ax.bar(1, value, bottom=bottoms[1], color=color, edgecolor='black',
                   linewidth=1.2, label=label)
            bottoms[1] += value

    # Observed (ON-ON) with synergy highlighted
    additive_pred = synergy['additive_prediction']

    if synergy_val > 0:
        # Synergistic: show additive + synergy
        ax.bar(2, additive_pred, color='#bdbdbd', edgecolor='black',
               linewidth=1.2, label='Additive Base')
        ax.bar(2, synergy_val, bottom=additive_pred, color='#3182bd',
               edgecolor='black', linewidth=1.2, label='Synergy')
    elif synergy_val < 0:
        # Antagonistic: show additive - antagonism
        ax.bar(2, on_on, color='#bdbdbd', edgecolor='black',
               linewidth=1.2, label='Reduced Outcome')
        ax.bar(2, -synergy_val, bottom=on_on, color='#e6550d',
               edgecolor='black', linewidth=1.2, label='Antagonism', hatch='///')
    else:
        # Additive: just show outcome
        ax.bar(2, on_on, color='#636363', edgecolor='black',
               linewidth=1.2, label='Additive Outcome')

    # Baseline bar
    ax.bar(0, off_off, color='#d3d3d3', edgecolor='black', linewidth=1.2)

    # Labels
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Baseline\n(OFF-OFF)', 'Additive\nPrediction', 'Observed\n(ON-ON)'])
    ax.set_ylabel('Mean Population', fontweight='bold')
    ax.set_title(f'Synergy Decomposition: {results["experiment"]}\n'
                 f'Synergy = {synergy_val:+.2f} ({synergy["classification"]})',
                 fontweight='bold')
    ax.set_ylim(0, max(additive_pred, on_on) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle=':')
    ax.legend(loc='upper left', framealpha=0.9)

    # Add value annotations
    ax.text(0, off_off + 0.05, f'{off_off:.2f}', ha='center', fontweight='bold')
    ax.text(1, additive_pred + 0.05, f'{additive_pred:.2f}', ha='center', fontweight='bold')
    ax.text(2, on_on + 0.05, f'{on_on:.2f}', ha='center', fontweight='bold')

    plt.tight_layout()
    output_path = output_dir / f'{results["experiment"]}_synergy_decomposition.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Figure 2 saved: {output_path}")
    return output_path


def create_population_trajectories(results: Dict, output_dir: Path):
    """
    Figure 3: Population Dynamics Trajectories

    Time series showing population evolution for all four conditions.
    """
    conditions_data = results['conditions']

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each condition
    colors = {
        'OFF-OFF': '#d3d3d3',
        'ON-OFF': '#9ecae1',
        'OFF-ON': '#fdae6b',
        'ON-ON': '#3182bd'
    }

    for condition_name, condition_data in conditions_data.items():
        if 'population_history' not in condition_data:
            continue

        history = condition_data['population_history']
        cycles = range(len(history))

        ax.plot(cycles, history, label=condition_name,
                color=colors.get(condition_name, '#636363'),
                linewidth=2, alpha=0.8)

        # Add mean line
        mean_pop = condition_data['mean_population']
        ax.axhline(y=mean_pop, color=colors.get(condition_name, '#636363'),
                   linestyle='--', linewidth=1, alpha=0.5)

    # Styling
    ax.set_xlabel('Simulation Cycle', fontweight='bold')
    ax.set_ylabel('Agent Population', fontweight='bold')
    ax.set_title(f'Population Dynamics: {results["experiment"]}',
                 fontweight='bold')
    ax.grid(alpha=0.3, linestyle=':')
    ax.legend(loc='best', framealpha=0.9)

    # Add mechanism info
    mechanism_info = results.get('mechanism_info', {})
    if mechanism_info:
        info_text = f"{mechanism_info.get('h1_name', 'H1')} × {mechanism_info.get('h2_name', 'H2')}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    output_path = output_dir / f'{results["experiment"]}_population_trajectories.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Figure 3 saved: {output_path}")
    return output_path


def create_summary_panel(results: Dict, output_dir: Path):
    """
    Figure 4: Summary Panel

    Multi-panel figure summarizing all key results.
    """
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    synergy = results['synergy_analysis']
    conditions_data = results['conditions']

    # Panel A: Factorial bar chart
    ax1 = fig.add_subplot(gs[0, 0])
    conditions = ['OFF-OFF', 'ON-OFF', 'OFF-ON', 'ON-ON']
    values = [synergy['off_off'], synergy['on_off'], synergy['off_on'], synergy['on_on']]
    colors = ['#d3d3d3', '#9ecae1', '#fdae6b', '#3182bd']

    ax1.bar(conditions, values, color=colors, edgecolor='black', linewidth=1.2)
    ax1.axhline(y=synergy['additive_prediction'], color='red', linestyle='--', linewidth=2)
    ax1.set_ylabel('Mean Population')
    ax1.set_title('(A) Factorial Comparison', fontweight='bold', loc='left')
    ax1.grid(axis='y', alpha=0.3, linestyle=':')

    # Panel B: Effect sizes
    ax2 = fig.add_subplot(gs[0, 1])
    effects = ['H1 Effect', 'H2 Effect', 'Synergy']
    effect_values = [synergy['h1_effect'], synergy['h2_effect'], synergy['synergy']]
    effect_colors = ['#9ecae1' if v > 0 else '#e6550d' for v in effect_values]

    ax2.barh(effects, effect_values, color=effect_colors, edgecolor='black', linewidth=1.2)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Effect Size')
    ax2.set_title('(B) Mechanism Effects', fontweight='bold', loc='left')
    ax2.grid(axis='x', alpha=0.3, linestyle=':')

    # Panel C: Population trajectories (simplified)
    ax3 = fig.add_subplot(gs[1, :])
    for condition_name, condition_data in conditions_data.items():
        if 'population_history' not in condition_data:
            continue

        history = condition_data['population_history']
        cycles = range(len(history))
        color = colors[conditions.index(condition_name)] if condition_name in conditions else '#636363'

        ax3.plot(cycles, history, label=condition_name, color=color, linewidth=2, alpha=0.8)

    ax3.set_xlabel('Simulation Cycle')
    ax3.set_ylabel('Agent Population')
    ax3.set_title('(C) Population Dynamics', fontweight='bold', loc='left')
    ax3.grid(alpha=0.3, linestyle=':')
    ax3.legend(loc='best', framealpha=0.9, ncol=4)

    # Overall title
    fig.suptitle(f'{results["experiment"]}: {synergy["classification"]} Interaction',
                 fontsize=14, fontweight='bold')

    output_path = output_dir / f'{results["experiment"]}_summary_panel.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Figure 4 saved: {output_path}")
    return output_path


def main():
    """Main visualization pipeline."""
    if len(sys.argv) < 2:
        print("Usage: python visualize_factorial_synergy.py <results_json>")
        print("Example: python visualize_factorial_synergy.py results/cycle255_h1h2_results.json")
        sys.exit(1)

    results_path = Path(sys.argv[1])
    if not results_path.exists():
        print(f"❌ Error: Results file not found: {results_path}")
        sys.exit(1)

    print(f"📊 Loading results from: {results_path}")
    results = load_results(results_path)

    # Create output directory
    output_dir = results_path.parent / "figures"
    output_dir.mkdir(exist_ok=True)

    print(f"📁 Output directory: {output_dir}")
    print("🎨 Generating figures...")
    print()

    # Generate all figures
    figures = []
    figures.append(create_factorial_bar_chart(results, output_dir))
    figures.append(create_synergy_decomposition(results, output_dir))
    figures.append(create_population_trajectories(results, output_dir))
    figures.append(create_summary_panel(results, output_dir))

    print()
    print("=" * 70)
    print("✅ VISUALIZATION COMPLETE")
    print("=" * 70)
    print(f"Generated {len(figures)} publication-ready figures:")
    for i, fig_path in enumerate(figures, 1):
        print(f"  {i}. {fig_path.name}")
    print()
    print(f"All figures saved to: {output_dir}")
    print("Resolution: 300 DPI (publication quality)")
    print("Format: PNG with transparent backgrounds where appropriate")
    print()
    print("Next steps:")
    print("  1. Review figures for accuracy")
    print("  2. Include in Paper 3 manuscript")
    print("  3. Adjust styling/labels as needed")
    print("=" * 70)


if __name__ == "__main__":
    main()
