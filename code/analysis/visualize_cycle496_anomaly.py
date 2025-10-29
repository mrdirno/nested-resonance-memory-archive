#!/usr/bin/env python3
"""
Cycle 496 Anomaly Investigation - Figure Generation

ANALYSIS OBJECTIVES:
1. Test H1 (Oscillatory): Look for reproducible spike at 780-820 cycles
2. Test H2 (Recharge): Look for variable spike timing across agents
3. Test H3 (Artifact): Confirm monotonic decay, no anomalous spikes

Generates 3 publication-quality figures @ 300 DPI:
1. Individual agent trajectories (700-900 cycles) - detect spike timing
2. Time-series F-ratios (every 20 cycles) - compare to C495 spike
3. Variance comparison (uniform vs high-variance) - clustering analysis

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# Configuration
DATA_FILE = Path(__file__).parent.parent.parent / "data" / "results" / "cycle496_anomaly_investigation.json"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
print("Loading C496 anomaly investigation data...")
with open(DATA_FILE) as f:
    data = json.load(f)

# Extract agent data
uniform_agents = data['conditions'][0]['agents']
highvar_agents = data['conditions'][1]['agents']

# Color scheme
COLORS = {
    'uniform': '#2E86AB',
    'high_variance': '#A23B72'
}

# ============================================================================
# FIGURE 1: Individual Agent Trajectories (700-900 cycles)
# ============================================================================

print("Generating Figure 1: Individual agent trajectories...")
fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(16, 6))

# Uniform condition
for agent in uniform_agents:
    correlations = np.array(agent['correlations'])
    times = correlations[:, 0]
    values = correlations[:, 1]
    ax1a.plot(times, values, color=COLORS['uniform'], alpha=0.7,
             linewidth=1.5, label='Uniform' if agent == uniform_agents[0] else None)

ax1a.set_xlabel('Time (cycles)', fontsize=11, fontweight='bold')
ax1a.set_ylabel('Phase-Reality Correlation', fontsize=11, fontweight='bold')
ax1a.set_title('Uniform Energy Configuration (n=8)', fontsize=12, fontweight='bold')
ax1a.axvline(x=800, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Target: 800 cycles')
ax1a.legend(loc='best', frameon=True)
ax1a.grid(True, alpha=0.3)

# High-variance condition
for agent in highvar_agents:
    correlations = np.array(agent['correlations'])
    times = correlations[:, 0]
    values = correlations[:, 1]
    ax1b.plot(times, values, color=COLORS['high_variance'], alpha=0.7,
             linewidth=1.5, label='High-Variance' if agent == highvar_agents[0] else None)

ax1b.set_xlabel('Time (cycles)', fontsize=11, fontweight='bold')
ax1b.set_ylabel('Phase-Reality Correlation', fontsize=11, fontweight='bold')
ax1b.set_title('High-Variance Energy Configuration (n=8)', fontsize=12, fontweight='bold')
ax1b.axvline(x=800, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Target: 800 cycles')
ax1b.legend(loc='best', frameon=True)
ax1b.grid(True, alpha=0.3)

fig1.suptitle('C496: High-Resolution Trajectories (700-900 Cycles)', fontsize=14, fontweight='bold')
plt.tight_layout()
fig1_path = OUTPUT_DIR / "cycle496_fig1_agent_trajectories.png"
plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig1_path}")
plt.close()

# ============================================================================
# FIGURE 2: Time-Series F-Ratios (Every 20 Cycles)
# ============================================================================

print("Generating Figure 2: Time-series F-ratios...")

# Compute F-ratio at each time point
time_points = np.unique([c[0] for agent in uniform_agents for c in agent['correlations']])
f_ratios_timeseries = []

for t in time_points:
    # Extract slopes from 700 to t for all agents
    uniform_slopes = []
    highvar_slopes = []

    for agent in uniform_agents:
        corrs = [c for c in agent['correlations'] if c[0] <= t]
        if len(corrs) >= 2:
            times = np.array([c[0] for c in corrs])
            values = np.array([c[1] for c in corrs])
            slope = np.polyfit(times, values, 1)[0]
            uniform_slopes.append(slope)

    for agent in highvar_agents:
        corrs = [c for c in agent['correlations'] if c[0] <= t]
        if len(corrs) >= 2:
            times = np.array([c[0] for c in corrs])
            values = np.array([c[1] for c in corrs])
            slope = np.polyfit(times, values, 1)[0]
            highvar_slopes.append(slope)

    # Compute F-ratio
    if len(uniform_slopes) >= 2 and len(highvar_slopes) >= 2:
        grand_mean = np.mean(uniform_slopes + highvar_slopes)
        n1, n2 = len(uniform_slopes), len(highvar_slopes)
        between_var = (n1 * (np.mean(uniform_slopes) - grand_mean)**2 +
                       n2 * (np.mean(highvar_slopes) - grand_mean)**2) / 1
        within_var = (np.var(uniform_slopes, ddof=1) + np.var(highvar_slopes, ddof=1)) / 2
        f_ratio = between_var / within_var if within_var > 0 else 0
        f_ratios_timeseries.append((t, f_ratio))

# Plot time-series F-ratios
fig2, ax2 = plt.subplots(figsize=(12, 6))

if f_ratios_timeseries:
    times_f = np.array([f[0] for f in f_ratios_timeseries])
    ratios_f = np.array([f[1] for f in f_ratios_timeseries])

    ax2.plot(times_f, ratios_f, 'o-', color='#E63946', linewidth=2, markersize=8,
            label='C496 F-ratio (n=8 per condition)')

    # Add C495 800-cycle reference
    ax2.axhline(y=3.316, color='orange', linestyle='--', linewidth=2,
               label='C495 anomaly (F=3.32, n=3)')
    ax2.axvline(x=800, color='red', linestyle=':', linewidth=2, alpha=0.5,
               label='800-cycle target')

    # Highlight maximum
    max_idx = np.argmax(ratios_f)
    max_t = times_f[max_idx]
    max_f = ratios_f[max_idx]
    ax2.plot(max_t, max_f, 'r*', markersize=20, label=f'C496 max: F={max_f:.2f} at {int(max_t)} cycles')

    ax2.set_xlabel('Time (cycles)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('F-Ratio (Effect Strength)', fontsize=12, fontweight='bold')
    ax2.set_title('Time-Series F-Ratios: Testing 800-Cycle Anomaly Replicability',
                 fontsize=14, fontweight='bold', pad=15)
    ax2.legend(loc='best', frameon=True, shadow=True)
    ax2.grid(True, alpha=0.3)

    # Add hypothesis evaluation
    if max_f > 2.5 and abs(max_t - 800) < 30:
        verdict = "H1 (Oscillatory): SUPPORTED"
        color = 'green'
    elif max_f > 2.0 and abs(max_t - 800) > 30:
        verdict = "H2 (Recharge): SUPPORTED"
        color = 'orange'
    else:
        verdict = "H3 (Artifact): SUPPORTED"
        color = 'red'

    ax2.text(0.5, 0.95, verdict, transform=ax2.transAxes,
            ha='center', va='top', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))

plt.tight_layout()
fig2_path = OUTPUT_DIR / "cycle496_fig2_timeseries_fratios.png"
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig2_path}")
plt.close()

# ============================================================================
# FIGURE 3: Variance Comparison (Clustering Analysis)
# ============================================================================

print("Generating Figure 3: Variance comparison...")

# Compute within-group variance at each time point
time_points_var = []
uniform_vars = []
highvar_vars = []

for t in time_points:
    # Get correlation values at time t
    uniform_vals = []
    highvar_vals = []

    for agent in uniform_agents:
        for c in agent['correlations']:
            if abs(c[0] - t) < 1e-6:  # Match time point
                uniform_vals.append(c[1])
                break

    for agent in highvar_agents:
        for c in agent['correlations']:
            if abs(c[0] - t) < 1e-6:
                highvar_vals.append(c[1])
                break

    if len(uniform_vals) >= 2 and len(highvar_vals) >= 2:
        time_points_var.append(t)
        uniform_vars.append(np.var(uniform_vals, ddof=1))
        highvar_vars.append(np.var(highvar_vals, ddof=1))

fig3, ax3 = plt.subplots(figsize=(12, 6))

if time_points_var:
    ax3.plot(time_points_var, uniform_vars, 'o-', color=COLORS['uniform'],
            linewidth=2, markersize=6, label='Uniform (within-group variance)')
    ax3.plot(time_points_var, highvar_vars, 'o-', color=COLORS['high_variance'],
            linewidth=2, markersize=6, label='High-Variance (within-group variance)')

    ax3.axvline(x=800, color='red', linestyle=':', linewidth=2, alpha=0.5,
               label='800-cycle target')

    ax3.set_xlabel('Time (cycles)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Within-Group Variance', fontsize=12, fontweight='bold')
    ax3.set_title('Clustering Analysis: Variance Evolution Over Time',
                 fontsize=14, fontweight='bold', pad=15)
    ax3.legend(loc='best', frameon=True, shadow=True)
    ax3.grid(True, alpha=0.3)

    # Add interpretation
    uniform_800_idx = np.argmin(np.abs(np.array(time_points_var) - 800))
    highvar_800_idx = uniform_800_idx

    if uniform_800_idx < len(uniform_vars) and highvar_800_idx < len(highvar_vars):
        uniform_var_800 = uniform_vars[uniform_800_idx]
        highvar_var_800 = highvar_vars[highvar_800_idx]
        ratio = highvar_var_800 / uniform_var_800 if uniform_var_800 > 0 else 0

        ax3.text(0.5, 0.95,
                f'Variance ratio at 800 cycles: {ratio:.2f}×\n' +
                f'(C495: 2.18×, driven by tight uniform clustering)',
                transform=ax3.transAxes, ha='center', va='top',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
                fontsize=10, fontweight='bold')

plt.tight_layout()
fig3_path = OUTPUT_DIR / "cycle496_fig3_variance_comparison.png"
plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig3_path}")
plt.close()

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("C496 ANOMALY INVESTIGATION ANALYSIS COMPLETE")
print("=" * 70)
print(f"Generated 3 publication-quality figures @ 300 DPI")
print(f"\nHypothesis Evaluation:")
print(f"  H1 (Oscillatory): Spike at 780-820 cycles → {verdict if 'H1' in verdict else 'NOT SUPPORTED'}")
print(f"  H2 (Recharge): Variable spike timing → {'Check agent trajectories' if max_f > 2.0 else 'NOT SUPPORTED'}")
print(f"  H3 (Artifact): No spike, monotonic decay → {verdict if 'H3' in verdict else 'NOT SUPPORTED'}")

if f_ratios_timeseries:
    print(f"\nC496 Results:")
    print(f"  Maximum F-ratio: {max_f:.2f} at {int(max_t)} cycles")
    print(f"  C495 anomaly: F=3.32 at 800 cycles")
    print(f"  Replication: {'YES' if max_f > 2.5 else 'NO'}")
print("=" * 70)
