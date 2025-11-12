#!/usr/bin/env python3
"""
Generate Figures for "When Network Topology Matters" Paper
===========================================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (AI Research Assistant)
Date: 2025-11-11 (Cycle 1474)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0

Generates 6 publication-quality figures @ 300 DPI for topology synthesis paper:

Figure 1: Network topology comparison (Scale-Free, Random, Lattice)
Figure 2: C187 baseline spawn invariance (bar plot with error bars)
Figure 3: C188 inequality-advantage dissociation (2-panel: Gini vs spawn rate)
Figure 4: C189 spatial composition inversion (bar plot, inverted ordering)
Figure 5: Mechanism comparison (3-panel: spatial, memory, threshold)
Figure 6: Unified synthesis diagram (composition vs spawn dynamics)

Usage:
    python generate_topology_paper_figures.py

Output:
    All figures saved to /Volumes/dual/DUALITY-ZERO-V2/data/figures/topology_paper/
    Files: figure1_networks.png, figure2_c187_invariance.png, ..., figure6_synthesis.png
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx
from scipy import stats

# ============================================================================
# CONFIGURATION
# ============================================================================

# Input data paths
DATA_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
C187_DATA = DATA_DIR / "c187_network_structure.json"
C188_DATA = DATA_DIR / "c188_energy_transport.json"
C189_DATA = DATA_DIR / "c189" / "c189_alternative_mechanisms.json"

# Output directory
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/topology_paper")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Figure settings
DPI = 300
FIGSIZE_SINGLE = (8, 6)
FIGSIZE_DOUBLE = (12, 5)
FIGSIZE_TRIPLE = (15, 5)

# Colors
COLOR_SF = '#e74c3c'  # Scale-Free (red)
COLOR_RANDOM = '#3498db'  # Random (blue)
COLOR_LATTICE = '#2ecc71'  # Lattice (green)

# Font settings
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['figure.titlesize'] = 18

# ============================================================================
# DATA LOADING
# ============================================================================

def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON data file."""
    print(f"Loading: {path}")
    with open(path, 'r') as f:
        data = json.load(f)
    print(f"  Loaded {len(data.get('experiments', data.get('results', [])))} experiments")
    return data

# ============================================================================
# FIGURE 1: NETWORK TOPOLOGY COMPARISON
# ============================================================================

def generate_figure1_networks():
    """
    Generate Figure 1: Network topology comparison
    3-panel: Scale-Free, Random, Lattice with statistics
    """
    print("\n" + "="*80)
    print("FIGURE 1: Network Topology Comparison")
    print("="*80)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    n_nodes = 100
    seed = 42

    # Scale-Free (Barabási-Albert)
    G_sf = nx.barabasi_albert_graph(n_nodes, m=2, seed=seed)
    pos_sf = nx.spring_layout(G_sf, seed=seed, k=0.3, iterations=50)
    degrees_sf = [G_sf.degree(n) for n in G_sf.nodes()]

    nx.draw_networkx_nodes(G_sf, pos_sf, ax=axes[0],
                           node_color=degrees_sf,
                           node_size=50,
                           cmap='Reds',
                           vmin=0, vmax=max(degrees_sf))
    nx.draw_networkx_edges(G_sf, pos_sf, ax=axes[0],
                           alpha=0.2, width=0.5)
    axes[0].set_title('Scale-Free\n(Barabási-Albert)', fontsize=14, fontweight='bold')
    axes[0].axis('off')

    # Add statistics
    diameter_sf = nx.diameter(G_sf)
    avg_degree_sf = np.mean(degrees_sf)
    axes[0].text(0.5, -0.05, f'Diameter: {diameter_sf}\nMean Degree: {avg_degree_sf:.2f}',
                 ha='center', va='top', transform=axes[0].transAxes,
                 fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Random (Erdős-Rényi)
    G_random = nx.erdos_renyi_graph(n_nodes, p=0.04, seed=seed)
    pos_random = nx.spring_layout(G_random, seed=seed, k=0.3, iterations=50)
    degrees_random = [G_random.degree(n) for n in G_random.nodes()]

    nx.draw_networkx_nodes(G_random, pos_random, ax=axes[1],
                           node_color=degrees_random,
                           node_size=50,
                           cmap='Blues',
                           vmin=0, vmax=max(degrees_random))
    nx.draw_networkx_edges(G_random, pos_random, ax=axes[1],
                           alpha=0.2, width=0.5)
    axes[1].set_title('Random\n(Erdős-Rényi)', fontsize=14, fontweight='bold')
    axes[1].axis('off')

    # Add statistics
    diameter_random = nx.diameter(G_random) if nx.is_connected(G_random) else 'N/A'
    avg_degree_random = np.mean(degrees_random)
    axes[1].text(0.5, -0.05, f'Diameter: {diameter_random}\nMean Degree: {avg_degree_random:.2f}',
                 ha='center', va='top', transform=axes[1].transAxes,
                 fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Lattice (2D Grid)
    G_lattice = nx.grid_2d_graph(10, 10, periodic=True)
    pos_lattice = {node: node for node in G_lattice.nodes()}
    degrees_lattice = [G_lattice.degree(n) for n in G_lattice.nodes()]

    nx.draw_networkx_nodes(G_lattice, pos_lattice, ax=axes[2],
                           node_color=degrees_lattice,
                           node_size=50,
                           cmap='Greens',
                           vmin=0, vmax=max(degrees_lattice))
    nx.draw_networkx_edges(G_lattice, pos_lattice, ax=axes[2],
                           alpha=0.2, width=0.5)
    axes[2].set_title('Lattice\n(2D Grid)', fontsize=14, fontweight='bold')
    axes[2].axis('off')

    # Add statistics
    diameter_lattice = 9  # For 10x10 torus
    avg_degree_lattice = np.mean(degrees_lattice)
    axes[2].text(0.5, -0.05, f'Diameter: {diameter_lattice}\nMean Degree: {avg_degree_lattice:.2f}',
                 ha='center', va='top', transform=axes[2].transAxes,
                 fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.suptitle('Figure 1: Network Topology Comparison (N=100 nodes)',
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()

    output_path = OUTPUT_DIR / "figure1_networks.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

# ============================================================================
# FIGURE 2: C187 BASELINE SPAWN INVARIANCE
# ============================================================================

def generate_figure2_c187_invariance():
    """
    Generate Figure 2: C187 baseline spawn invariance
    Bar plot with error bars showing identical spawn rates
    """
    print("\n" + "="*80)
    print("FIGURE 2: C187 Baseline Spawn Invariance")
    print("="*80)

    # Load C187 data
    data = load_json(C187_DATA)
    experiments = data.get('experiments', data.get('results', []))

    # Extract spawn rates by topology
    topologies = ['scale_free', 'random', 'lattice']
    spawn_rates = {topo: [] for topo in topologies}

    for exp in experiments:
        topo = exp.get('topology', '').lower().replace('-', '_')
        if topo in spawn_rates:
            spawn_rate = exp.get('spawn_rate', exp.get('final_spawn_rate', 0))
            if spawn_rate > 0:
                spawn_rates[topo].append(spawn_rate)

    # Calculate statistics
    means = [np.mean(spawn_rates[t]) for t in topologies]
    stds = [np.std(spawn_rates[t], ddof=1) for t in topologies]
    ns = [len(spawn_rates[t]) for t in topologies]
    sems = [stds[i] / np.sqrt(ns[i]) for i in range(3)]

    # 95% confidence intervals
    ci_95 = [1.96 * sem for sem in sems]

    print(f"\nStatistics:")
    for i, topo in enumerate(topologies):
        print(f"  {topo.replace('_', '-').title():12s}: {means[i]:.6f} ± {ci_95[i]:.6f} (n={ns[i]})")

    # Create plot
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    x = np.arange(3)
    colors = [COLOR_SF, COLOR_RANDOM, COLOR_LATTICE]
    labels = ['Scale-Free', 'Random', 'Lattice']

    bars = ax.bar(x, means, yerr=ci_95,
                  color=colors, alpha=0.7,
                  capsize=10, error_kw={'linewidth': 2})

    # Add value labels on bars
    for i, (bar, mean, ci) in enumerate(zip(bars, means, ci_95)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + ci + 0.00005,
                f'{mean:.6f}\n±{ci:.6f}',
                ha='center', va='bottom', fontsize=10)

    ax.set_ylabel('Spawn Rate (spawns/agent/cycle)', fontsize=14)
    ax.set_xlabel('Network Topology', fontsize=14)
    ax.set_title('Figure 2: C187 Baseline Spawn Invariance\n(p = 0.999, F = 0.00087)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim([0, max(means) * 1.15])

    # Add statistical annotation
    ax.text(0.5, 0.95, 'Topology does NOT affect spawn rates at baseline\nANOVA: p = 0.999',
            transform=ax.transAxes, ha='center', va='top',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "figure2_c187_invariance.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

# ============================================================================
# FIGURE 3: C188 INEQUALITY-ADVANTAGE DISSOCIATION
# ============================================================================

def generate_figure3_c188_dissociation():
    """
    Generate Figure 3: C188 inequality-advantage dissociation
    2-panel: (A) Energy Gini coefficient, (B) Spawn rates
    """
    print("\n" + "="*80)
    print("FIGURE 3: C188 Inequality-Advantage Dissociation")
    print("="*80)

    # Load C188 data
    data = load_json(C188_DATA)
    experiments = data.get('experiments', data.get('results', []))

    # Filter for r_transport = 1.0 (maximum transport)
    exp_max_transport = [e for e in experiments if abs(e.get('transport_rate', 0) - 1.0) < 0.01]

    # Extract by topology
    topologies = ['scale_free', 'random', 'lattice']
    gini = {t: [] for t in topologies}
    spawn_rate = {t: [] for t in topologies}

    for exp in exp_max_transport:
        topo = exp.get('topology', '').lower().replace('-', '_')
        if topo in gini:
            gini[topo].append(exp.get('energy_gini', 0))
            spawn_rate[topo].append(exp.get('spawn_rate', 0))

    # Calculate statistics
    gini_means = [np.mean(gini[t]) for t in topologies]
    gini_stds = [np.std(gini[t], ddof=1) for t in topologies]
    spawn_means = [np.mean(spawn_rate[t]) for t in topologies]
    spawn_stds = [np.std(spawn_rate[t], ddof=1) for t in topologies]

    print(f"\nEnergy Gini (transport_rate=1.0):")
    for i, t in enumerate(topologies):
        print(f"  {t.replace('_', '-').title():12s}: {gini_means[i]:.4f} ± {gini_stds[i]:.4f}")

    print(f"\nSpawn Rate (transport_rate=1.0):")
    for i, t in enumerate(topologies):
        print(f"  {t.replace('_', '-').title():12s}: {spawn_means[i]:.6f} ± {spawn_stds[i]:.6f}")

    # Create 2-panel plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIGSIZE_DOUBLE)

    x = np.arange(3)
    colors = [COLOR_SF, COLOR_RANDOM, COLOR_LATTICE]
    labels = ['Scale-Free', 'Random', 'Lattice']

    # Panel A: Energy Gini
    ax1.bar(x, gini_means, yerr=gini_stds, color=colors, alpha=0.7, capsize=10)
    ax1.set_ylabel('Energy Gini Coefficient', fontsize=12)
    ax1.set_xlabel('Network Topology', fontsize=12)
    ax1.set_title('(A) Energy Inequality\n(p < 10⁻⁷, CONFIRMED)', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=15, ha='right')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Add significance stars
    ax1.text(0, gini_means[0] + gini_stds[0] + 0.01, '***', ha='center', fontsize=16, color='red')

    # Panel B: Spawn Rate
    ax2.bar(x, spawn_means, yerr=spawn_stds, color=colors, alpha=0.7, capsize=10)
    ax2.set_ylabel('Spawn Rate (spawns/agent/cycle)', fontsize=12)
    ax2.set_xlabel('Network Topology', fontsize=12)
    ax2.set_title('(B) Spawn Advantage\n(p = 0.999, FALSIFIED)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=15, ha='right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # Add "no difference" annotation
    ax2.text(0.5, 0.95, 'No difference', transform=ax2.transAxes,
             ha='center', va='top', fontsize=11,
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    plt.suptitle('Figure 3: C188 Inequality-Advantage Dissociation\nResource Inequality ≠ Fitness Inequality',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = OUTPUT_DIR / "figure3_c188_dissociation.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

# ============================================================================
# FIGURE 4: C189 SPATIAL COMPOSITION INVERSION
# ============================================================================

def generate_figure4_c189_inversion():
    """
    Generate Figure 4: C189 spatial composition inversion
    Bar plot showing inverted ordering: Lattice > SF > Random
    """
    print("\n" + "="*80)
    print("FIGURE 4: C189 Spatial Composition Inversion")
    print("="*80)

    # Load C189 data
    data = load_json(C189_DATA)
    experiments = data.get('experiments', data.get('results', []))

    # Filter for spatial composition mechanism
    exp_spatial = [e for e in experiments if e.get('mechanism', '') == 'spatial']

    # Extract by topology
    topologies = ['scale_free', 'random', 'lattice']
    comp_rates = {t: [] for t in topologies}

    for exp in exp_spatial:
        topo = exp.get('topology', '').lower().replace('-', '_')
        if topo in comp_rates:
            rate = exp.get('composition_rate', 0)
            if rate > 0:
                comp_rates[topo].append(rate * 100)  # Convert to percentage

    # Calculate statistics
    means = [np.mean(comp_rates[t]) for t in topologies]
    stds = [np.std(comp_rates[t], ddof=1) for t in topologies]
    ns = [len(comp_rates[t]) for t in topologies]

    print(f"\nComposition Rates (Spatial Mechanism):")
    for i, t in enumerate(topologies):
        print(f"  {t.replace('_', '-').title():12s}: {means[i]:.1f}% ± {stds[i]:.1f}% (n={ns[i]})")

    # Reorder for visual clarity: Lattice > Scale-Free > Random
    order = [2, 0, 1]  # lattice, scale_free, random
    means_ordered = [means[i] for i in order]
    stds_ordered = [stds[i] for i in order]
    colors_ordered = [COLOR_LATTICE, COLOR_SF, COLOR_RANDOM]
    labels_ordered = ['Lattice', 'Scale-Free', 'Random']

    # Create plot
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    x = np.arange(3)
    bars = ax.bar(x, means_ordered, yerr=stds_ordered,
                  color=colors_ordered, alpha=0.7, capsize=10)

    # Add value labels
    for bar, mean, std in zip(bars, means_ordered, stds_ordered):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 2,
                f'{mean:.1f}%\n±{std:.1f}%',
                ha='center', va='bottom', fontsize=10)

    ax.set_ylabel('Composition Rate (%)', fontsize=14)
    ax.set_xlabel('Network Topology', fontsize=14)
    ax.set_title('Figure 4: C189 Spatial Composition Inversion\n(p < 3e-07, d = 5.20, INVERTED FROM PREDICTION)',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels_ordered)
    ax.set_ylim([0, 100])

    # Add explanation box
    explanation = 'INVERTED ORDERING:\nLonger diameter → Lower normalized distance\n→ Higher composition probability'
    ax.text(0.98, 0.50, explanation, transform=ax.transAxes,
            ha='right', va='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

    # Add significance annotations
    ax.plot([0, 1], [92, 92], 'k-', lw=1.5)
    ax.text(0.5, 93, '***', ha='center', fontsize=16, color='red')
    ax.plot([1, 2], [75, 75], 'k-', lw=1.5)
    ax.text(1.5, 76, '***', ha='center', fontsize=16, color='red')

    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()

    output_path = OUTPUT_DIR / "figure4_c189_inversion.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

# ============================================================================
# FIGURE 5: MECHANISM COMPARISON
# ============================================================================

def generate_figure5_mechanism_comparison():
    """
    Generate Figure 5: Mechanism comparison across C189
    3-panel: Spatial (effect), Memory (null), Threshold (null)
    """
    print("\n" + "="*80)
    print("FIGURE 5: Mechanism Comparison")
    print("="*80)

    # Load C189 data
    data = load_json(C189_DATA)
    experiments = data.get('experiments', data.get('results', []))

    # Extract data by mechanism and topology
    mechanisms = ['spatial', 'memory', 'threshold']
    topologies = ['scale_free', 'random', 'lattice']

    # Data structures
    comp_rates = {m: {t: [] for t in topologies} for m in mechanisms}
    spawn_rates = {m: {t: [] for t in topologies} for m in mechanisms}

    for exp in experiments:
        mech = exp.get('mechanism', '')
        topo = exp.get('topology', '').lower().replace('-', '_')

        if mech in mechanisms and topo in topologies:
            comp_rate = exp.get('composition_rate', 0)
            if comp_rate > 0:
                comp_rates[mech][topo].append(comp_rate * 100)

            spawn_rate = exp.get('spawn_rate', 0)
            if spawn_rate > 0:
                spawn_rates[mech][topo].append(spawn_rate)

    # Create 3-panel plot
    fig, axes = plt.subplots(1, 3, figsize=FIGSIZE_TRIPLE)

    colors = [COLOR_SF, COLOR_RANDOM, COLOR_LATTICE]
    labels = ['Scale-Free', 'Random', 'Lattice']
    x = np.arange(3)

    # Panel A: Spatial Composition (show composition rates)
    means_spatial = [np.mean(comp_rates['spatial'][t]) for t in topologies]
    stds_spatial = [np.std(comp_rates['spatial'][t], ddof=1) for t in topologies]

    axes[0].bar(x, means_spatial, yerr=stds_spatial, color=colors, alpha=0.7, capsize=8)
    axes[0].set_ylabel('Composition Rate (%)', fontsize=11)
    axes[0].set_xlabel('Topology', fontsize=11)
    axes[0].set_title('(A) Spatial Composition\np < 3e-07 ✓', fontsize=11, fontweight='bold')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=15, ha='right', fontsize=9)
    axes[0].set_ylim([0, 100])
    axes[0].grid(axis='y', alpha=0.3, linestyle='--')
    axes[0].text(0.5, 0.95, 'EFFECT', transform=axes[0].transAxes,
                 ha='center', va='top', fontsize=10, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

    # Panel B: Memory Transport (show spawn rates)
    means_memory = [np.mean(spawn_rates['memory'][t]) * 1000 for t in topologies]  # Scale to milli
    stds_memory = [np.std(spawn_rates['memory'][t], ddof=1) * 1000 for t in topologies]

    axes[1].bar(x, means_memory, yerr=stds_memory, color=colors, alpha=0.7, capsize=8)
    axes[1].set_ylabel('Spawn Rate (×10⁻³)', fontsize=11)
    axes[1].set_xlabel('Topology', fontsize=11)
    axes[1].set_title('(B) Memory Transport\np = 0.999 ✗', fontsize=11, fontweight='bold')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=15, ha='right', fontsize=9)
    axes[1].grid(axis='y', alpha=0.3, linestyle='--')
    axes[1].text(0.5, 0.95, 'NULL', transform=axes[1].transAxes,
                 ha='center', va='top', fontsize=10, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

    # Panel C: Threshold Scaling (show spawn rates)
    means_threshold = [np.mean(spawn_rates['threshold'][t]) * 1000 for t in topologies]
    stds_threshold = [np.std(spawn_rates['threshold'][t], ddof=1) * 1000 for t in topologies]

    axes[2].bar(x, means_threshold, yerr=stds_threshold, color=colors, alpha=0.7, capsize=8)
    axes[2].set_ylabel('Spawn Rate (×10⁻³)', fontsize=11)
    axes[2].set_xlabel('Topology', fontsize=11)
    axes[2].set_title('(C) Threshold Scaling\np = 1.000 ✗', fontsize=11, fontweight='bold')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels, rotation=15, ha='right', fontsize=9)
    axes[2].grid(axis='y', alpha=0.3, linestyle='--')
    axes[2].text(0.5, 0.95, 'NULL', transform=axes[2].transAxes,
                 ha='center', va='top', fontsize=10, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

    plt.suptitle('Figure 5: Mechanism Comparison Across C189\nOnly Spatial Composition Creates Topology Effects',
                 fontsize=13, fontweight='bold', y=1.00)
    plt.tight_layout()

    output_path = OUTPUT_DIR / "figure5_mechanism_comparison.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

# ============================================================================
# FIGURE 6: UNIFIED SYNTHESIS DIAGRAM
# ============================================================================

def generate_figure6_synthesis():
    """
    Generate Figure 6: Unified synthesis diagram
    Conceptual diagram showing composition vs spawn dynamics
    """
    print("\n" + "="*80)
    print("FIGURE 6: Unified Synthesis Diagram")
    print("="*80)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, 'When Network Topology Matters',
            ha='center', va='top', fontsize=20, fontweight='bold')
    ax.text(5, 9.0, 'Composition Dynamics vs Spawn Dynamics',
            ha='center', va='top', fontsize=14, style='italic')

    # Top panel: Composition Processes (TOPOLOGY MATTERS)
    rect_comp = mpatches.FancyBboxPatch((0.5, 6.0), 9, 2.5,
                                        boxstyle="round,pad=0.1",
                                        edgecolor='green', facecolor='lightgreen',
                                        linewidth=3, alpha=0.3)
    ax.add_patch(rect_comp)

    ax.text(5, 8.2, 'COMPOSITION PROCESSES', ha='center', va='top',
            fontsize=16, fontweight='bold', color='darkgreen')
    ax.text(5, 7.8, 'Topology MATTERS ✓', ha='center', va='top',
            fontsize=13, fontweight='bold', color='green')

    ax.text(1, 7.3, '• Spatial proximity-weighted interaction',
            ha='left', va='top', fontsize=11)
    ax.text(1, 6.9, '• Network geometry affects interaction probability',
            ha='left', va='top', fontsize=11)
    ax.text(1, 6.5, '• Inverted ordering: Lattice > Scale-Free > Random',
            ha='left', va='top', fontsize=11)
    ax.text(1, 6.1, '• Mechanism: Long diameter → high composition rate',
            ha='left', va='top', fontsize=11, style='italic')

    # Arrow down
    ax.annotate('', xy=(5, 5.8), xytext=(5, 6.0),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5.3, 5.9, 'Does NOT translate to', ha='left', va='center',
            fontsize=11, fontweight='bold')

    # Bottom panel: Spawn Processes (TOPOLOGY DOESN'T MATTER)
    rect_spawn = mpatches.FancyBboxPatch((0.5, 2.5), 9, 3.0,
                                         boxstyle="round,pad=0.1",
                                         edgecolor='red', facecolor='lightcoral',
                                         linewidth=3, alpha=0.3)
    ax.add_patch(rect_spawn)

    ax.text(5, 5.3, 'SPAWN PROCESSES', ha='center', va='top',
            fontsize=16, fontweight='bold', color='darkred')
    ax.text(5, 4.9, 'Topology DOES NOT MATTER ✗', ha='center', va='top',
            fontsize=13, fontweight='bold', color='red')

    ax.text(1, 4.4, '• Energy accumulation at hubs → No spawn advantage',
            ha='left', va='top', fontsize=11)
    ax.text(1, 4.0, '• Memory accumulation at hubs → No spawn advantage',
            ha='left', va='top', fontsize=11)
    ax.text(1, 3.6, '• Threshold modulation by energy → No spawn advantage',
            ha='left', va='top', fontsize=11)
    ax.text(1, 3.2, '• Spawn rates identical: Scale-Free = Random = Lattice',
            ha='left', va='top', fontsize=11)
    ax.text(1, 2.8, '• Dissociation: Resource inequality ≠ Fitness inequality',
            ha='left', va='top', fontsize=11, style='italic', fontweight='bold')

    # Bottom explanation
    rect_explain = mpatches.FancyBboxPatch((0.5, 0.2), 9, 2.0,
                                           boxstyle="round,pad=0.1",
                                           edgecolor='blue', facecolor='lightblue',
                                           linewidth=2, alpha=0.2)
    ax.add_patch(rect_explain)

    ax.text(5, 2.0, 'Four Equalizing Mechanisms:', ha='center', va='top',
            fontsize=13, fontweight='bold', color='darkblue')
    ax.text(5, 1.6, '1. Population Capacity Constraints  •  2. Stochastic Equalization',
            ha='center', va='top', fontsize=10)
    ax.text(5, 1.3, '3. Threshold Saturation  •  4. Network Rewiring',
            ha='center', va='top', fontsize=10)
    ax.text(5, 0.9, 'These mechanisms decouple structural advantage from fitness advantage',
            ha='center', va='top', fontsize=10, style='italic')

    # Core insight box
    ax.text(5, 0.3, 'Core Insight: Topology matters for HOW agents interact, NOT whether they succeed',
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', edgecolor='black', linewidth=2))

    plt.tight_layout()

    output_path = OUTPUT_DIR / "figure6_synthesis.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all 6 figures for topology paper."""
    print("\n" + "="*80)
    print("GENERATING FIGURES FOR 'WHEN NETWORK TOPOLOGY MATTERS' PAPER")
    print("="*80)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Resolution: {DPI} DPI")
    print(f"Total figures: 6")

    try:
        # Generate all figures
        generate_figure1_networks()
        generate_figure2_c187_invariance()
        generate_figure3_c188_dissociation()
        generate_figure4_c189_inversion()
        generate_figure5_mechanism_comparison()
        generate_figure6_synthesis()

        print("\n" + "="*80)
        print("✓ ALL FIGURES GENERATED SUCCESSFULLY")
        print("="*80)
        print(f"\nOutput files:")
        for i in range(1, 7):
            figure_name = f"figure{i}_*.png"
            matching_files = list(OUTPUT_DIR.glob(f"figure{i}_*.png"))
            if matching_files:
                for f in matching_files:
                    size_mb = f.stat().st_size / (1024 * 1024)
                    print(f"  {f.name:35s} {size_mb:6.2f} MB")

        print(f"\nTotal output directory size:")
        total_size = sum(f.stat().st_size for f in OUTPUT_DIR.glob("*.png"))
        print(f"  {total_size / (1024 * 1024):.2f} MB")

        print("\nNext steps:")
        print("  1. Review figures visually")
        print("  2. Copy to git repository: papers/compiled/topology_paper/")
        print("  3. Update topology paper with figure captions")
        print("  4. Commit to GitHub")
        print("  5. Proceed with LaTeX conversion and arXiv submission")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
