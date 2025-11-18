#!/usr/bin/env python3
"""
C186 V6b Campaign Results Analysis
Net-Positive Energy Growth Regime

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-18
Cycle: 1378
"""

import json
import pandas as pd
from pathlib import Path
from scipy import stats
import numpy as np

# Paths
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")

# Load all V6b results
results = []
for json_file in sorted(RESULTS_DIR.glob("c186_v6b_HIERARCHICAL_GROWTH_*.json")):
    with open(json_file, 'r') as f:
        data = json.load(f)
        results.append({
            'condition': data['condition'],
            'seed': data['seed'],
            'f_spawn': data['parameters']['f_spawn'],
            'final_pop': data['results']['final_population'],
            'final_energy': data['results']['final_energy'],
            'runtime_seconds': data['results']['runtime_seconds'],
            'success': data['results']['success']
        })

df = pd.DataFrame(results)

print("=" * 80)
print("C186 V6b CAMPAIGN RESULTS - NET-POSITIVE GROWTH REGIME")
print("=" * 80)
print()

# Overall statistics
print("OVERALL STATISTICS:")
print(f"Total experiments: {len(df)}")
print(f"Success rate: {df['success'].sum()}/{len(df)} ({df['success'].mean()*100:.1f}%)")
print(f"Mean population: {df['final_pop'].mean():.1f} ± {df['final_pop'].std():.1f}")
print(f"Population range: {df['final_pop'].min():.0f} - {df['final_pop'].max():.0f}")
print(f"Mean energy: {df['final_energy'].mean():.1f} ± {df['final_energy'].std():.1f}")
print(f"Mean runtime: {df['runtime_seconds'].mean():.2f} ± {df['runtime_seconds'].std():.2f} seconds")
print()

# Statistics by spawn rate
print("=" * 80)
print("STATISTICS BY SPAWN RATE:")
print("=" * 80)
print()

spawn_rates = sorted(df['f_spawn'].unique())
for f_spawn in spawn_rates:
    subset = df[df['f_spawn'] == f_spawn]
    pct = f_spawn * 100
    print(f"Spawn Rate: {pct:.2f}% (f = {f_spawn})")
    print(f"  n = {len(subset)}")
    print(f"  Population: {subset['final_pop'].mean():.1f} ± {subset['final_pop'].std():.1f}")
    print(f"  Energy: {subset['final_energy'].mean():.1f} ± {subset['final_energy'].std():.1f}")
    print(f"  Runtime: {subset['runtime_seconds'].mean():.2f} ± {subset['runtime_seconds'].std():.2f}s")
    print()

# ANOVA test
print("=" * 80)
print("SPAWN RATE EFFECT (ONE-WAY ANOVA):")
print("=" * 80)
print()

groups = [df[df['f_spawn'] == rate]['final_pop'].values for rate in spawn_rates]
f_stat, p_value = stats.f_oneway(*groups)

print(f"F-statistic: {f_stat:.3f}")
print(f"p-value: {p_value:.3f}")
print()

if p_value < 0.05:
    print("✓ Significant spawn rate effect (p < 0.05)")
    print("  → Spawn rate DOES influence final population in growth regime")
else:
    print("✗ No significant spawn rate effect (p ≥ 0.05)")
    print("  → Spawn rate independence confirmed (like V6a)")
print()

# Energy cap analysis
print("=" * 80)
print("ENERGY CAP ANALYSIS:")
print("=" * 80)
print()

ENERGY_CAP = 10_000_000
at_cap = df[df['final_energy'] >= ENERGY_CAP]
print(f"Experiments at energy cap (≥10M): {len(at_cap)}/{len(df)} ({len(at_cap)/len(df)*100:.1f}%)")
print(f"Mean energy (all): {df['final_energy'].mean():.1f}")
print(f"Min energy: {df['final_energy'].min():.1f}")
print(f"Max energy: {df['final_energy'].max():.1f}")
print()

# Runtime comparison to V6a
print("=" * 80)
print("RUNTIME COMPARISON (V6b vs V6a expectations):")
print("=" * 80)
print()
print("V6b actual runtime:")
print(f"  Mean: {df['runtime_seconds'].mean():.2f} seconds")
print(f"  Range: {df['runtime_seconds'].min():.2f} - {df['runtime_seconds'].max():.2f} seconds")
print()
print("V6a reference (from previous campaign):")
print(f"  Mean: ~22 seconds (full 450,000 cycles)")
print()
print(f"Speedup: {22 / df['runtime_seconds'].mean():.1f}× faster (due to energy cap early termination)")
print()

# Export summary
summary = {
    'campaign': 'C186_V6b_NET_POSITIVE_GROWTH',
    'total_experiments': len(df),
    'success_rate': float(df['success'].mean()),
    'mean_population': float(df['final_pop'].mean()),
    'std_population': float(df['final_pop'].std()),
    'mean_energy': float(df['final_energy'].mean()),
    'std_energy': float(df['final_energy'].std()),
    'mean_runtime_seconds': float(df['runtime_seconds'].mean()),
    'anova_f_statistic': float(f_stat),
    'anova_p_value': float(p_value),
    'spawn_rate_effect': 'significant' if p_value < 0.05 else 'not_significant',
    'experiments_at_energy_cap': int(len(at_cap)),
    'energy_cap_percentage': float(len(at_cap)/len(df))
}

summary_path = RESULTS_DIR / "v6b_analysis_summary.json"
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"Summary exported: {summary_path}")
print()
