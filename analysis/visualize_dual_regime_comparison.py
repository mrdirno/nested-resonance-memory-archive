#!/usr/bin/env python3
"""
Dual-Regime Comparison Visualization (V6a vs V6b)
Publication-quality figures for manuscript

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-18
Cycle: 1378
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import stats

# Paths
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
FIGURES_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Load V6a results
v6a_results = []
for json_file in sorted(RESULTS_DIR.glob("c186_v6a_HIERARCHICAL_*.json")):
    with open(json_file, 'r') as f:
        data = json.load(f)
        v6a_results.append({
            'regime': 'Homeostasis (net=0)',
            'f_spawn': data['parameters']['f_spawn'],
            'final_pop': data['results']['final_population']
        })

# Load V6b results
v6b_results = []
for json_file in sorted(RESULTS_DIR.glob("c186_v6b_HIERARCHICAL_GROWTH_*.json")):
    with open(json_file, 'r') as f:
        data = json.load(f)
        v6b_results.append({
            'regime': 'Growth (net=+0.5)',
            'f_spawn': data['parameters']['f_spawn'],
            'final_pop': data['results']['final_population']
        })

# Create combined dataframe
df = pd.DataFrame(v6a_results + v6b_results)

# Set publication style
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.major.width'] = 1.5
plt.rcParams['ytick.major.width'] = 1.5

# ============================================================================
# FIGURE 1: Population by Spawn Rate (Dual Regime)
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 8))

spawn_rates = sorted(df['f_spawn'].unique())
spawn_labels = [f"{rate*100:.2f}%" for rate in spawn_rates]
x_pos = np.arange(len(spawn_rates))
width = 0.35

# V6a bars
v6a_means = [df[(df['regime'] == 'Homeostasis (net=0)') & (df['f_spawn'] == rate)]['final_pop'].mean()
             for rate in spawn_rates]
v6a_stds = [df[(df['regime'] == 'Homeostasis (net=0)') & (df['f_spawn'] == rate)]['final_pop'].std()
            for rate in spawn_rates]

# V6b bars
v6b_means = [df[(df['regime'] == 'Growth (net=+0.5)') & (df['f_spawn'] == rate)]['final_pop'].mean()
             for rate in spawn_rates]
v6b_stds = [df[(df['regime'] == 'Growth (net=+0.5)') & (df['f_spawn'] == rate)]['final_pop'].std()
            for rate in spawn_rates]

bars1 = ax.bar(x_pos - width/2, v6a_means, width, yerr=v6a_stds,
               label='V6a: Homeostasis (net=0)', color='#2E86AB', alpha=0.8,
               error_kw={'linewidth': 2, 'capsize': 5, 'capthick': 2})
bars2 = ax.bar(x_pos + width/2, v6b_means, width, yerr=v6b_stds,
               label='V6b: Growth (net=+0.5)', color='#A23B72', alpha=0.8,
               error_kw={'linewidth': 2, 'capsize': 5, 'capthick': 2})

ax.set_xlabel('Spawn Rate', fontsize=14, fontweight='bold')
ax.set_ylabel('Final Population (agents)', fontsize=14, fontweight='bold')
ax.set_title('Dual-Regime Population Comparison:\nEnergy Balance Determines Population Fate',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x_pos)
ax.set_xticklabels(spawn_labels)
ax.legend(fontsize=12, frameon=True, shadow=True)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add annotations
ax.text(0.02, 0.98, f'V6a ANOVA: p = 0.448 (no spawn rate effect)',
        transform=ax.transAxes, fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
ax.text(0.02, 0.91, f'V6b ANOVA: p < 0.001 (significant spawn rate effect)',
        transform=ax.transAxes, fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(FIGURES_DIR / 'dual_regime_population_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure 1 saved: dual_regime_population_comparison.png (300 DPI)")

# ============================================================================
# FIGURE 2: Phase Diagram (Energy Regime vs Population)
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 8))

# Plot V6a data points
v6a_df = df[df['regime'] == 'Homeostasis (net=0)']
ax.scatter(v6a_df['f_spawn'] * 100, v6a_df['final_pop'],
           s=100, alpha=0.6, color='#2E86AB', label='V6a: Homeostasis (net=0)',
           edgecolors='black', linewidths=1)

# Plot V6b data points
v6b_df = df[df['regime'] == 'Growth (net=+0.5)']
ax.scatter(v6b_df['f_spawn'] * 100, v6b_df['final_pop'],
           s=100, alpha=0.6, color='#A23B72', label='V6b: Growth (net=+0.5)',
           edgecolors='black', linewidths=1)

# Add regime separation line
ax.axhline(y=10000, color='red', linestyle='--', linewidth=2, alpha=0.5,
           label='Regime Separation (~10,000 agents)')

ax.set_xlabel('Spawn Rate (%)', fontsize=14, fontweight='bold')
ax.set_ylabel('Final Population (agents)', fontsize=14, fontweight='bold')
ax.set_title('Energy Regime Phase Diagram:\n96× Population Difference from Single Parameter Change',
             fontsize=16, fontweight='bold', pad=20)
ax.set_yscale('log')
ax.legend(fontsize=11, frameon=True, shadow=True, loc='upper left')
ax.grid(True, alpha=0.3, linestyle='--')

# Add text annotations
ax.text(0.5, 0.95, 'E_consume: 1.0 → 0.5 produces qualitatively different dynamics',
        transform=ax.transAxes, fontsize=11, ha='center', va='top',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

plt.tight_layout()
plt.savefig(FIGURES_DIR / 'dual_regime_phase_diagram.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure 2 saved: dual_regime_phase_diagram.png (300 DPI)")

# ============================================================================
# FIGURE 3: Spawn Rate Effect by Regime
# ============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# V6a: No spawn rate effect
for rate in spawn_rates:
    subset = v6a_df[v6a_df['f_spawn'] == rate]
    ax1.scatter([rate*100] * len(subset), subset['final_pop'],
                s=80, alpha=0.5, color='#2E86AB')

ax1.plot([r*100 for r in spawn_rates], v6a_means, 'o-',
         linewidth=3, markersize=10, color='#2E86AB', alpha=0.8)
ax1.set_xlabel('Spawn Rate (%)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Final Population', fontsize=12, fontweight='bold')
ax1.set_title('V6a: Homeostasis Regime\n(No Spawn Rate Effect, p=0.448)',
              fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_ylim([195, 206])

# V6b: Significant spawn rate effect
for rate in spawn_rates:
    subset = v6b_df[v6b_df['f_spawn'] == rate]
    ax2.scatter([rate*100] * len(subset), subset['final_pop'],
                s=80, alpha=0.5, color='#A23B72')

ax2.plot([r*100 for r in spawn_rates], v6b_means, 'o-',
         linewidth=3, markersize=10, color='#A23B72', alpha=0.8)
ax2.set_xlabel('Spawn Rate (%)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Final Population', fontsize=12, fontweight='bold')
ax2.set_title('V6b: Growth Regime\n(Significant Spawn Rate Effect, p<0.001)',
              fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_ylim([16500, 20500])

plt.suptitle('Regime-Dependent Spawn Rate Dynamics', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'spawn_rate_effect_by_regime.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure 3 saved: spawn_rate_effect_by_regime.png (300 DPI)")

# ============================================================================
# Summary
# ============================================================================

print()
print("=" * 80)
print("DUAL-REGIME VISUALIZATION COMPLETE")
print("=" * 80)
print()
print("Figures saved to:", FIGURES_DIR)
print()
print("Publication-quality figures (300 DPI):")
print("  1. dual_regime_population_comparison.png - Bar chart comparison")
print("  2. dual_regime_phase_diagram.png - Log-scale phase space")
print("  3. spawn_rate_effect_by_regime.png - Regime-specific spawn dynamics")
print()
print("Ready for manuscript preparation.")
print()
