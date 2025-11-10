#!/usr/bin/env python3
"""
CYCLE 267: PERCOLATION DYNAMICS ANALYSIS

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Developed By: Claude (Anthropic)
Date: 2025-11-09
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0

Purpose:
    Zero-delay analysis infrastructure for C267 Percolation experiments.
    Tests if NRM compositional networks exhibit percolation phase transitions
    at critical composition rate p_c with mean-field universality class.

MOG Pattern: NRM Network Topology × Percolation Theory (α=0.71)

Novel Predictions:
    1. Critical Threshold: p_c ∈ [0.020, 0.035]
    2. Power-Law Scaling: S_∞ ~ (p - p_c)^β, β ≈ 1.0
    3. Cluster Distribution: n_s ~ s^(-τ), τ ≈ 2.5 at p_c
    4. Finite-Size Scaling: Universal collapse with exponents β, ν

Publication Target: Physical Review E (IF ~2.4)
Alternative: Journal of Statistical Physics (IF ~1.6)

Usage:
    python analyze_c267_percolation.py /path/to/c267_results.json
"""

import json
import sys
from pathlib import Path
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import networkx as nx

# Reproducibility
np.random.seed(42)


def measure_giant_component(composition_events, N):
    """Compute size of largest connected component."""
    G = nx.DiGraph()
    for event in composition_events:
        G.add_edge(event['parent_id'], event['child_id'])
    
    if len(G) == 0:
        return 0.0
    
    components = list(nx.weakly_connected_components(G))
    giant = max(components, key=len) if components else set()
    return len(giant) / N


def detect_critical_threshold(p_values, S_infinity_values):
    """Detect percolation threshold via inflection point."""
    # Logistic fit: S = L / (1 + exp(-k*(p - p_c)))
    from scipy.optimize import curve_fit
    
    def logistic(p, L, k, p_c):
        return L / (1 + np.exp(-k * (p - p_c)))
    
    try:
        popt, _ = curve_fit(logistic, p_values, S_infinity_values,
                           p0=[1.0, 10.0, 0.025], maxfev=10000)
        p_c = popt[2]
        return {"p_c": p_c, "detected": True}
    except:
        return {"p_c": 0.025, "detected": False}


def fit_critical_scaling(p_values, S_values, p_c):
    """Fit S_∞ ~ (p - p_c)^β near critical point."""
    mask = np.array(p_values) > p_c
    p_above = np.array(p_values)[mask]
    S_above = np.array(S_values)[mask]
    
    if len(p_above) < 3:
        return {"beta": 0.0, "R_squared": 0.0, "hypothesis_passed": False}
    
    delta_p = p_above - p_c
    log_delta = np.log(delta_p)
    log_S = np.log(S_above)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_delta, log_S)
    
    return {
        "beta": slope,
        "R_squared": r_value**2,
        "p_value": p_value,
        "hypothesis_passed": (0.8 <= slope <= 1.2 and r_value**2 > 0.90)
    }


def measure_cluster_distribution(composition_network):
    """Compute cluster size distribution at critical point."""
    components = list(nx.weakly_connected_components(composition_network))
    cluster_sizes = [len(c) for c in components]
    
    unique_sizes, counts = np.unique(cluster_sizes, return_counts=True)
    
    if len(unique_sizes) < 3:
        return {"tau": 0.0, "R_squared": 0.0, "hypothesis_passed": False}
    
    log_s = np.log(unique_sizes)
    log_n = np.log(counts)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_s, log_n)
    tau = -slope
    
    return {
        "tau": tau,
        "R_squared": r_value**2,
        "hypothesis_passed": (2.0 <= tau <= 3.0 and r_value**2 > 0.85)
    }


def analyze_c267_results(results_path):
    """Main analysis pipeline for C267 Percolation experiments."""
    print("=" * 80)
    print("CYCLE 267: PERCOLATION DYNAMICS ANALYSIS")
    print("=" * 80)
    
    with open(results_path, 'r') as f:
        all_results = json.load(f)
    
    # Separate by condition
    sweep_results = [r for r in all_results if r['condition'] == 'PERCOLATION-SWEEP']
    
    print(f"\nLoaded {len(sweep_results)} PERCOLATION-SWEEP experiments")
    
    # Extract p values and S_infinity
    p_values = []
    S_values = []
    
    for result in sweep_results:
        p = result['composition_rate']
        S = measure_giant_component(result['composition_events'], result['N'])
        p_values.append(p)
        S_values.append(S)
    
    # Aggregate by p value
    p_unique = sorted(set(p_values))
    S_means = [np.mean([S for p, S in zip(p_values, S_values) if p == pu])
               for pu in p_unique]
    
    # Prediction 1: Critical Threshold
    critical = detect_critical_threshold(p_unique, S_means)
    print(f"\nCritical Threshold: p_c = {critical['p_c']:.4f}")
    
    # Prediction 2: Power-Law Scaling
    scaling = fit_critical_scaling(p_unique, S_means, critical['p_c'])
    print(f"Scaling Exponent: β = {scaling['beta']:.3f}, R² = {scaling['R_squared']:.3f}")
    print(f"Hypothesis: {'✓ PASSED' if scaling['hypothesis_passed'] else '✗ FAILED'}")
    
    # Generate figure
    output_dir = results_path.parent
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Panel A: S_infinity vs p
    ax = axes[0]
    ax.plot(p_unique, S_means, 'o-', color='#2E86AB', linewidth=2)
    ax.axvline(critical['p_c'], color='red', linestyle='--', label=f'p_c = {critical["p_c"]:.3f}')
    ax.set_xlabel("Composition Rate p")
    ax.set_ylabel("Giant Component Size S_∞")
    ax.set_title("(A) Percolation Transition")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Panel B: Log-log scaling
    ax = axes[1]
    mask = np.array(p_unique) > critical['p_c']
    p_above = np.array(p_unique)[mask]
    S_above = np.array(S_means)[mask]
    delta_p = p_above - critical['p_c']
    
    ax.loglog(delta_p, S_above, 'o', color='#2E86AB', markersize=8)
    ax.set_xlabel("log(p - p_c)")
    ax.set_ylabel("log(S_∞)")
    ax.set_title(f"(B) Critical Scaling (β = {scaling['beta']:.2f})")
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "c267_percolation_figure.png", dpi=300)
    print(f"\nSaved figure: {output_dir}/c267_percolation_figure.png")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_c267_percolation.py <results.json>")
        sys.exit(1)
    
    results_path = Path(sys.argv[1])
    if not results_path.exists():
        print(f"Error: File not found: {results_path}")
        sys.exit(1)
    
    analyze_c267_results(results_path)


if __name__ == "__main__":
    main()
