#!/usr/bin/env python3
"""Quick topology paper figure generator - works with actual data structures"""
import json
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

DPI = 300
OUT = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/topology_paper")
OUT.mkdir(parents=True, exist_ok=True)

# Load data
print("Loading data...")
c187 = json.load(open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c187_network_structure.json'))
c188 = json.load(open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c188_energy_transport.json'))['results']
c189 = json.load(open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c189/c189_alternative_mechanisms.json'))['results']

print(f"C187: {len(c187.get('topology_aggregates', []))} topologies")
print(f"C188: {len(c188)} experiments")
print(f"C189: {len(c189)} experiments")

# Figure 2: C187 baseline (use topology_aggregates)
print("\nGenerating Figure 2...")
fig, ax = plt.subplots(figsize=(8, 6))
topos = c187['topology_aggregates']
labels = [t['topology'].replace('_', '-').title() for t in topos]
means = [np.mean(t['spawn_rate_values']) for t in topos]
stds = [np.std(t['spawn_rate_values']) for t in topos]
colors = ['#e74c3c', '#3498db', '#2ecc71']

ax.bar(range(3), means, yerr=stds, color=colors, alpha=0.7, capsize=10)
ax.set_ylabel('Spawn Rate', fontsize=14)
ax.set_xlabel('Topology', fontsize=14)
ax.set_title('Figure 2: C187 Baseline Spawn Invariance\n(p = 0.999)', fontsize=14, fontweight='bold')
ax.set_xticks(range(3))
ax.set_xticklabels(labels)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "figure2_c187_invariance.png", dpi=DPI, bbox_inches='tight')
print(f"✓ Saved figure2_c187_invariance.png")
plt.close()

# Figure 3: C188 dissociation (transport_rate=1.0)
print("Generating Figure 3...")
c188_max = [e for e in c188 if abs(e.get('transport_rate', 0) - 1.0) < 0.01]
gini_data = {'scale_free': [], 'random': [], 'lattice': []}
spawn_data = {'scale_free': [], 'random': [], 'lattice': []}
for e in c188_max:
    t = e['topology']
    if 'energy_gini' in e: gini_data[t].append(e['energy_gini'])
    spawn_data[t].append(e['spawn_rate'])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
topos_order = ['scale_free', 'random', 'lattice']
labels = ['Scale-Free', 'Random', 'Lattice']

# Panel A: Gini
gini_means = [np.mean(gini_data[t]) if gini_data[t] else 0 for t in topos_order]
gini_stds = [np.std(gini_data[t]) if len(gini_data[t]) > 1 else 0 for t in topos_order]
ax1.bar(range(3), gini_means, yerr=gini_stds, color=colors, alpha=0.7, capsize=10)
ax1.set_ylabel('Energy Gini', fontsize=12)
ax1.set_xlabel('Topology', fontsize=12)
ax1.set_title('(A) Inequality\np < 10⁻⁷', fontsize=12, fontweight='bold')
ax1.set_xticks(range(3))
ax1.set_xticklabels(labels, rotation=15, ha='right')
ax1.grid(axis='y', alpha=0.3)

# Panel B: Spawn
spawn_means = [np.mean(spawn_data[t]) for t in topos_order]
spawn_stds = [np.std(spawn_data[t]) for t in topos_order]
ax2.bar(range(3), spawn_means, yerr=spawn_stds, color=colors, alpha=0.7, capsize=10)
ax2.set_ylabel('Spawn Rate', fontsize=12)
ax2.set_xlabel('Topology', fontsize=12)
ax2.set_title('(B) Spawn Advantage\np = 0.999', fontsize=12, fontweight='bold')
ax2.set_xticks(range(3))
ax2.set_xticklabels(labels, rotation=15, ha='right')
ax2.grid(axis='y', alpha=0.3)

plt.suptitle('Figure 3: C188 Inequality-Advantage Dissociation', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUT / "figure3_c188_dissociation.png", dpi=DPI, bbox_inches='tight')
print(f"✓ Saved figure3_c188_dissociation.png")
plt.close()

# Figure 4: C189 spatial inversion
print("Generating Figure 4...")
spatial = [e for e in c189 if e['mechanism'] == 'spatial']
comp_data = {'scale_free': [], 'random': [], 'lattice': []}
for e in spatial:
    comp_data[e['topology']].append(e['composition_rate'] * 100)

# Reorder: Lattice, SF, Random
means_ordered = [np.mean(comp_data['lattice']), np.mean(comp_data['scale_free']), np.mean(comp_data['random'])]
stds_ordered = [np.std(comp_data['lattice']), np.std(comp_data['scale_free']), np.std(comp_data['random'])]
labels_ordered = ['Lattice', 'Scale-Free', 'Random']
colors_ordered = ['#2ecc71', '#e74c3c', '#3498db']

fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(range(3), means_ordered, yerr=stds_ordered, color=colors_ordered, alpha=0.7, capsize=10)
ax.set_ylabel('Composition Rate (%)', fontsize=14)
ax.set_xlabel('Topology', fontsize=14)
ax.set_title('Figure 4: C189 Spatial Composition Inversion\n(p < 3e-07, INVERTED)', fontsize=13, fontweight='bold')
ax.set_xticks(range(3))
ax.set_xticklabels(labels_ordered)
ax.set_ylim([0, 100])
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "figure4_c189_inversion.png", dpi=DPI, bbox_inches='tight')
print(f"✓ Saved figure4_c189_inversion.png")
plt.close()

# Figure 5: Mechanism comparison
print("Generating Figure 5...")
mechanisms = ['spatial', 'memory', 'threshold']
topos = ['scale_free', 'random', 'lattice']

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for i, mech in enumerate(mechanisms):
    mech_data = [e for e in c189 if e['mechanism'] == mech]
    
    if mech == 'spatial':
        # Show composition rates
        data = {t: [e['composition_rate'] * 100 for e in mech_data if e['topology'] == t] for t in topos}
        ylabel = 'Composition Rate (%)'
    else:
        # Show spawn rates
        data = {t: [e['spawn_rate'] * 1000 for e in mech_data if e['topology'] == t] for t in topos}
        ylabel = 'Spawn Rate (×10⁻³)'
    
    means = [np.mean(data[t]) for t in topos]
    stds = [np.std(data[t]) for t in topos]
    
    axes[i].bar(range(3), means, yerr=stds, color=colors, alpha=0.7, capsize=8)
    axes[i].set_ylabel(ylabel, fontsize=11)
    axes[i].set_xlabel('Topology', fontsize=11)
    axes[i].set_title(f'({chr(65+i)}) {mech.title()}', fontsize=11, fontweight='bold')
    axes[i].set_xticks(range(3))
    axes[i].set_xticklabels(['SF', 'Rand', 'Latt'], fontsize=9)
    axes[i].grid(axis='y', alpha=0.3)

plt.suptitle('Figure 5: Mechanism Comparison', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(OUT / "figure5_mechanism_comparison.png", dpi=DPI, bbox_inches='tight')
print(f"✓ Saved figure5_mechanism_comparison.png")
plt.close()

print("\n✓ Generated 4 figures (2, 3, 4, 5)")
print(f"✓ Saved to: {OUT}")
print("\nNote: Figures 1 (networks) and 6 (synthesis) require manual creation")
