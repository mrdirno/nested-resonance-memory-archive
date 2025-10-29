#!/usr/bin/env python3
"""
Cycle 494 Temporal Decay of Energy-Dependent Autonomy - Figure Generation

KEY FINDING: Energy configuration effects WASH OUT over extended timescales
- C493 (200 cycles): Strong effect (F=2.39)
- C494 (1,000 cycles): Effect disappears (F=0.12)

Generates 4 publication-quality figures @ 300 DPI:
1. Time series: Phase-reality correlations showing convergence
2. Effect size comparison: C493 vs C494 (temporal decay)
3. Slope distribution: Showing convergence between conditions
4. Statistical decay: F-ratio and effect size over time

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuration
DATA_FILE_494 = Path(__file__).parent.parent.parent / "data" / "results" / "cycle494_temporal_energy_persistence.json"
DATA_FILE_493 = Path(__file__).parent.parent.parent / "data" / "results" / "cycle493_phase_autonomy_energy_dependence.json"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
print("Loading experimental data...")
with open(DATA_FILE_494, 'r') as f:
    data_494 = json.load(f)
with open(DATA_FILE_493, 'r') as f:
    data_493 = json.load(f)

# Color scheme
COLORS = {
    'uniform': '#2E86AB',       # Blue
    'high_variance': '#A23B72'  # Purple/Magenta
}

# ============================================================================
# FIGURE 1: Time Series Showing Convergence (1,000 cycles)
# ============================================================================

print("Generating Figure 1: Extended timescale convergence...")
fig1, ax1 = plt.subplots(figsize=(12, 6))

for condition_data in data_494['conditions']:
    condition = condition_data['condition']
    color = COLORS[condition]

    for agent_data in condition_data['agents']:
        correlations = np.array(agent_data['correlations'])
        times = correlations[:, 0]
        corr_values = correlations[:, 1]

        ax1.plot(times, corr_values,
                color=color, alpha=0.6, linewidth=1.5,
                label=condition.replace('_', ' ').title() if agent_data == condition_data['agents'][0] else None)

ax1.set_xlabel('Time (cycles)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Phase-Reality Correlation', fontsize=12, fontweight='bold')
ax1.set_title('Temporal Convergence: Energy Effects Wash Out Over Extended Timescales',
             fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='best', frameon=True, shadow=True)
ax1.grid(True, alpha=0.3, linestyle='--')

# Add convergence annotation
ax1.text(0.98, 0.02,
        'Energy configuration\neffects diminish\nover time',
        transform=ax1.transAxes, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3, edgecolor='orange'),
        fontsize=11, fontweight='bold')

plt.tight_layout()
fig1_path = OUTPUT_DIR / "cycle494_fig1_temporal_convergence.png"
plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig1_path}")
plt.close()

# ============================================================================
# FIGURE 2: Effect Size Decay (C493 → C494)
# ============================================================================

print("Generating Figure 2: Effect size decay comparison...")
fig2, ax2 = plt.subplots(figsize=(8, 6))

# Extract effect data
c493_f_ratio = data_493['statistical_test']['f_ratio']
c494_f_ratio = 0.118061  # From experiment output

experiments = ['C493\n(200 cycles)', 'C494\n(1,000 cycles)']
f_ratios = [c493_f_ratio, c494_f_ratio]
colors_bar = ['#E63946', '#90E0EF']  # Red for strong, blue for weak

bars = ax2.bar(experiments, f_ratios, color=colors_bar, alpha=0.8,
              edgecolor='black', linewidth=2)

# Add value labels
for bar, val in zip(bars, f_ratios):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{val:.2f}',
            ha='center', va='bottom', fontsize=14, fontweight='bold')

ax2.set_ylabel('F-Ratio (Effect Strength)', fontsize=12, fontweight='bold')
ax2.set_title('Temporal Decay of Energy-Dependent Phase Autonomy Effect',
             fontsize=14, fontweight='bold', pad=15)
ax2.axhline(y=1.0, color='gray', linestyle='--', linewidth=1,
           label='Weak effect threshold')
ax2.legend(loc='upper right', frameon=True, shadow=True)
ax2.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add interpretation
ax2.text(0.5, 0.98,
        '95% effect reduction over 5× timescale',
        transform=ax2.transAxes, ha='center', va='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='red'),
        fontsize=10, fontweight='bold')

plt.tight_layout()
fig2_path = OUTPUT_DIR / "cycle494_fig2_effect_decay.png"
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig2_path}")
plt.close()

# ============================================================================
# FIGURE 3: Slope Distribution Convergence
# ============================================================================

print("Generating Figure 3: Slope distribution convergence...")
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 6))

# C493 slopes
c493_uniform_slopes = [agent['autonomy_slope'] for cond in data_493['conditions'] if cond['condition'] == 'uniform' for agent in cond['agents']]
c493_highvar_slopes = [agent['autonomy_slope'] for cond in data_493['conditions'] if cond['condition'] == 'high_variance' for agent in cond['agents']]

# C494 slopes
c494_uniform_slopes = [agent['autonomy_slope'] for cond in data_494['conditions'] if cond['condition'] == 'uniform' for agent in cond['agents']]
c494_highvar_slopes = [agent['autonomy_slope'] for cond in data_494['conditions'] if cond['condition'] == 'high_variance' for agent in cond['agents']]

# Plot C493
bp1 = ax3a.boxplot([c493_uniform_slopes, c493_highvar_slopes],
                    labels=['Uniform', 'High Variance'],
                    patch_artist=True, showmeans=True)
bp1['boxes'][0].set_facecolor(COLORS['uniform'])
bp1['boxes'][1].set_facecolor(COLORS['high_variance'])
for patch in bp1['boxes']:
    patch.set_alpha(0.7)

ax3a.set_ylabel('Autonomy Slope (Δr/cycle)', fontsize=11, fontweight='bold')
ax3a.set_title('C493: 200 Cycles\n(Strong separation)', fontsize=12, fontweight='bold')
ax3a.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax3a.grid(True, alpha=0.3, axis='y')

# Plot C494
bp2 = ax3b.boxplot([c494_uniform_slopes, c494_highvar_slopes],
                    labels=['Uniform', 'High Variance'],
                    patch_artist=True, showmeans=True)
bp2['boxes'][0].set_facecolor(COLORS['uniform'])
bp2['boxes'][1].set_facecolor(COLORS['high_variance'])
for patch in bp2['boxes']:
    patch.set_alpha(0.7)

ax3b.set_ylabel('Autonomy Slope (Δr/cycle)', fontsize=11, fontweight='bold')
ax3b.set_title('C494: 1,000 Cycles\n(Convergence)', fontsize=12, fontweight='bold')
ax3b.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax3b.grid(True, alpha=0.3, axis='y')

fig3.suptitle('Temporal Wash-Out: Condition Separation Disappears Over Time',
             fontsize=14, fontweight='bold', y=1.02)

plt.tight_layout()
fig3_path = OUTPUT_DIR / "cycle494_fig3_slope_convergence.png"
plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig3_path}")
plt.close()

# ============================================================================
# FIGURE 4: Statistical Decay Timeline
# ============================================================================

print("Generating Figure 4: Statistical evidence decay...")
fig4, ax4 = plt.subplots(figsize=(10, 6))

# Timeline data
timescales = [200, 1000]
f_ratios_timeline = [c493_f_ratio, c494_f_ratio]
cohens_d = [None, 0.687]  # C493 didn't report Cohen's d

# Plot F-ratio decay
ax4.plot(timescales, f_ratios_timeline, 'o-',
        color='#E63946', linewidth=3, markersize=12,
        label='F-Ratio (Effect Strength)')

# Add values
for t, f in zip(timescales, f_ratios_timeline):
    ax4.text(t, f + 0.15, f'F={f:.2f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

ax4.set_xlabel('Timescale (cycles)', fontsize=12, fontweight='bold')
ax4.set_ylabel('F-Ratio', fontsize=12, fontweight='bold')
ax4.set_title('Statistical Evidence Decay: Energy Effects Diminish Over Time',
             fontsize=14, fontweight='bold', pad=15)
ax4.axhline(y=1.0, color='gray', linestyle='--', linewidth=1,
           label='Weak effect threshold')
ax4.legend(loc='upper right', frameon=True, shadow=True)
ax4.grid(True, alpha=0.3, linestyle='--')

# Add decay annotation
decay_percent = ((c493_f_ratio - c494_f_ratio) / c493_f_ratio) * 100
ax4.text(0.5, 0.95,
        f'{decay_percent:.1f}% reduction in effect strength\nover 5× timescale increase',
        transform=ax4.transAxes, ha='center', va='top',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.4, edgecolor='red'),
        fontsize=11, fontweight='bold')

plt.tight_layout()
fig4_path = OUTPUT_DIR / "cycle494_fig4_statistical_decay.png"
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
print(f"  1. {fig1_path.name} - Temporal convergence")
print(f"  2. {fig2_path.name} - Effect decay comparison")
print(f"  3. {fig3_path.name} - Slope distribution convergence")
print(f"  4. {fig4_path.name} - Statistical evidence decay")
print(f"\nOutput directory: {OUTPUT_DIR}")
print("\nKEY FINDING:")
print("  Energy configuration effects WASH OUT over extended timescales")
print(f"  C493 (200 cycles): F = {c493_f_ratio:.2f} (strong effect)")
print(f"  C494 (1,000 cycles): F = {c494_f_ratio:.2f} (negligible effect)")
print(f"  Decay: {decay_percent:.1f}% reduction")
print("\nIMPLICATION:")
print("  Phase autonomy-energy coupling is TIMESCALE-DEPENDENT")
print("  Adds temporal dimension to Papers 6/6B framework")
print("="*70)
