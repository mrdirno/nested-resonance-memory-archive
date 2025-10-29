#!/usr/bin/env python3
"""
Cycle 493 Phase Autonomy Energy Dependence - Figure Generation

Generates 4 publication-quality figures @ 300 DPI:
1. Time series: Phase-reality correlations over time
2. Bar chart: Mean autonomy slope by condition
3. Scatter: Energy-autonomy relationship
4. Box plot: Statistical distribution comparison

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuration
DATA_FILE = Path(__file__).parent.parent.parent / "data" / "results" / "cycle493_phase_autonomy_energy_dependence.json"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
print("Loading C493 experimental data...")
with open(DATA_FILE, 'r') as f:
    data = json.load(f)

# Color scheme
COLORS = {
    'uniform': '#2E86AB',       # Blue
    'high_variance': '#A23B72',  # Purple/Magenta
    'low_energy': '#F18F01'      # Orange
}

CONDITION_LABELS = {
    'uniform': 'Uniform Energy (100)',
    'high_variance': 'High Variance (50, 100, 150)',
    'low_energy': 'Low Energy (30)'
}

# ============================================================================
# FIGURE 1: Time Series of Phase-Reality Correlations
# ============================================================================

print("Generating Figure 1: Time series...")
fig1, ax1 = plt.subplots(figsize=(10, 6))

for condition_data in data['conditions']:
    condition = condition_data['condition']
    color = COLORS[condition]

    for agent_data in condition_data['agents']:
        agent_id = agent_data['agent_id']
        correlations = np.array(agent_data['correlations'])
        times = correlations[:, 0]
        corr_values = correlations[:, 1]

        # Plot time series
        ax1.plot(times, corr_values,
                color=color, alpha=0.7, linewidth=1.5,
                label=CONDITION_LABELS[condition] if agent_data == condition_data['agents'][0] else None)

ax1.set_xlabel('Time (cycles)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Phase-Reality Correlation', fontsize=12, fontweight='bold')
ax1.set_title('Phase Autonomy Evolution Across Energy Conditions',
             fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='best', frameon=True, shadow=True)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_ylim([0.85, 1.0])

# Add horizontal line at mean
overall_mean = np.mean([agent_data['mean_correlation']
                        for cond in data['conditions']
                        for agent_data in cond['agents']])
ax1.axhline(y=overall_mean, color='gray', linestyle=':', linewidth=1,
           label=f'Overall Mean: {overall_mean:.3f}')

plt.tight_layout()
fig1_path = OUTPUT_DIR / "cycle493_fig1_time_series.png"
plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig1_path}")
plt.close()

# ============================================================================
# FIGURE 2: Mean Autonomy Slope by Condition (Bar Chart)
# ============================================================================

print("Generating Figure 2: Autonomy slope comparison...")
fig2, ax2 = plt.subplots(figsize=(8, 6))

conditions = []
mean_slopes = []
std_slopes = []
colors = []

for condition_data in data['conditions']:
    condition = condition_data['condition']
    conditions.append(CONDITION_LABELS[condition])
    mean_slopes.append(condition_data['mean_autonomy_slope'])
    std_slopes.append(condition_data['std_autonomy_slope'])
    colors.append(COLORS[condition])

x = np.arange(len(conditions))
bars = ax2.bar(x, mean_slopes, yerr=std_slopes,
              color=colors, alpha=0.8, capsize=10,
              edgecolor='black', linewidth=1.5)

# Add value labels on bars
for i, (bar, val, err) in enumerate(zip(bars, mean_slopes, std_slopes)):
    height = bar.get_height()
    sign = '+' if val > 0 else ''
    ax2.text(bar.get_x() + bar.get_width()/2., height + err + 0.00002,
            f'{sign}{val:.2e}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_ylabel('Mean Autonomy Slope (Δr/cycle)', fontsize=12, fontweight='bold')
ax2.set_title('Phase Autonomy Development Rate by Energy Configuration',
             fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(conditions, rotation=15, ha='right')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add interpretation text
f_ratio = data['statistical_test']['f_ratio']
ax2.text(0.98, 0.02, f'F-ratio = {f_ratio:.2f}\n(Strong evidence for\nenergy-dependent autonomy)',
        transform=ax2.transAxes, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray'),
        fontsize=9)

plt.tight_layout()
fig2_path = OUTPUT_DIR / "cycle493_fig2_slope_comparison.png"
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig2_path}")
plt.close()

# ============================================================================
# FIGURE 3: Energy-Autonomy Relationship (Scatter Plot)
# ============================================================================

print("Generating Figure 3: Energy-autonomy scatter...")
fig3, ax3 = plt.subplots(figsize=(8, 6))

for condition_data in data['conditions']:
    condition = condition_data['condition']
    color = COLORS[condition]

    for agent_data in condition_data['agents']:
        initial_energy = agent_data['initial_energy']
        autonomy_slope = agent_data['autonomy_slope']

        ax3.scatter(initial_energy, autonomy_slope,
                   color=color, s=150, alpha=0.7,
                   edgecolors='black', linewidths=1.5,
                   label=CONDITION_LABELS[condition] if agent_data == condition_data['agents'][0] else None)

ax3.set_xlabel('Initial Energy', fontsize=12, fontweight='bold')
ax3.set_ylabel('Autonomy Slope (Δr/cycle)', fontsize=12, fontweight='bold')
ax3.set_title('Phase Autonomy Development vs. Initial Energy',
             fontsize=14, fontweight='bold', pad=15)
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.legend(loc='best', frameon=True, shadow=True)

# Add annotation for key insight
ax3.text(0.98, 0.98,
        'Energy variance\n(not level)\npromotes autonomy',
        transform=ax3.transAxes, ha='right', va='top',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3, edgecolor='orange'),
        fontsize=10, fontweight='bold')

plt.tight_layout()
fig3_path = OUTPUT_DIR / "cycle493_fig3_energy_scatter.png"
plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig3_path}")
plt.close()

# ============================================================================
# FIGURE 4: Statistical Distribution Comparison (Box Plot)
# ============================================================================

print("Generating Figure 4: Distribution comparison...")
fig4, ax4 = plt.subplots(figsize=(8, 6))

# Collect all individual autonomy slopes by condition
box_data = []
box_labels = []
box_colors = []

for condition_data in data['conditions']:
    condition = condition_data['condition']
    slopes = [agent_data['autonomy_slope'] for agent_data in condition_data['agents']]
    box_data.append(slopes)
    box_labels.append(CONDITION_LABELS[condition])
    box_colors.append(COLORS[condition])

# Create box plot
bp = ax4.boxplot(box_data, labels=box_labels, patch_artist=True,
                showmeans=True, meanline=True,
                boxprops=dict(linewidth=1.5, edgecolor='black'),
                medianprops=dict(linewidth=2, color='red'),
                meanprops=dict(linewidth=2, color='blue', linestyle='--'),
                whiskerprops=dict(linewidth=1.5),
                capprops=dict(linewidth=1.5))

# Color boxes
for patch, color in zip(bp['boxes'], box_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax4.set_ylabel('Autonomy Slope (Δr/cycle)', fontsize=12, fontweight='bold')
ax4.set_title('Distribution of Phase Autonomy Development Rates',
             fontsize=14, fontweight='bold', pad=15)
ax4.set_xticklabels(box_labels, rotation=15, ha='right')
ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
ax4.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add legend for line types
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='red', linewidth=2, label='Median'),
    Line2D([0], [0], color='blue', linewidth=2, linestyle='--', label='Mean')
]
ax4.legend(handles=legend_elements, loc='upper right', frameon=True, shadow=True)

plt.tight_layout()
fig4_path = OUTPUT_DIR / "cycle493_fig4_distribution.png"
plt.savefig(fig4_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig4_path}")
plt.close()

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*70)
print("FIGURE GENERATION COMPLETE")
print("="*70)
print(f"Generated 4 publication-quality figures @ 300 DPI:")
print(f"  1. {fig1_path.name} - Time series")
print(f"  2. {fig2_path.name} - Slope comparison")
print(f"  3. {fig3_path.name} - Energy-autonomy scatter")
print(f"  4. {fig4_path.name} - Distribution box plot")
print(f"\nOutput directory: {OUTPUT_DIR}")
print("\nKey Finding:")
print("  Energy variance (high_variance condition) promotes phase autonomy")
print("  Uniform energy shows autonomy decay")
print(f"  F-ratio = {data['statistical_test']['f_ratio']:.2f}")
print("="*70)
