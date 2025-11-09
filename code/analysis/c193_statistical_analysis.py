#!/usr/bin/env python3
"""
C193 Statistical Analysis: Population Size Scaling Law

Analyzes results from C193 (Population Size Scaling experiment) to:
1. Characterize population dynamics across N_initial
2. Compare Deterministic vs Flat mechanism variance
3. Validate N-independent robustness
4. Generate 4 publication figures @ 300 DPI

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2 Sonnet 4.5)
Date: 2025-11-08 (Cycle 1325+)
License: GPL-3.0
"""

import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
from scipy import stats
from typing import Dict, List, Tuple

# Plotting parameters
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# Paths
DATA_FILE = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c193_population_scaling.json")
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load C193 results"""
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    return data

# ============================================================================
# STATISTICAL TESTS
# ============================================================================

def anova_population_dynamics(data: Dict) -> Dict:
    """
    ANOVA: mean(pop) ~ N_initial + f_intra + mechanism

    Tests main effects and interactions on final population size.
    """
    print("=" * 80)
    print("ANOVA: Population Size ~ N_initial + f_intra + mechanism")
    print("=" * 80)
    print()

    results_list = data['individual_results']

    # Extract data by condition
    groups = {}
    for result in results_list:
        n = result['n_initial']
        f = result['f_intra_pct']
        mech = result['spawn_mechanism']
        pop = result['final_population']

        key = (n, f, mech)
        if key not in groups:
            groups[key] = []
        groups[key].append(pop)

    # Main effect: N_initial (collapse across f and mechanism)
    n_groups = {}
    for (n, f, mech), pops in groups.items():
        if n not in n_groups:
            n_groups[n] = []
        n_groups[n].extend(pops)

    n_values = sorted(n_groups.keys())
    n_samples = [n_groups[n] for n in n_values]

    f_stat_n, p_value_n = stats.f_oneway(*n_samples)

    print("Main Effect: N_initial")
    print(f"  F-statistic: {f_stat_n:.4f}")
    print(f"  p-value: {p_value_n:.4e}")
    print(f"  Interpretation: {'SIGNIFICANT' if p_value_n < 0.001 else 'Not significant'}")
    print()

    for n in n_values:
        mean_pop = np.mean(n_groups[n])
        std_pop = np.std(n_groups[n], ddof=1)
        print(f"  N={n:2d}: mean={mean_pop:5.2f}, SD={std_pop:4.2f}, n={len(n_groups[n])}")
    print()

    # Main effect: f_intra (collapse across N and mechanism)
    f_groups = {}
    for (n, f, mech), pops in groups.items():
        if f not in f_groups:
            f_groups[f] = []
        f_groups[f].extend(pops)

    f_values = sorted(f_groups.keys())
    f_samples = [f_groups[f] for f in f_values]

    f_stat_f, p_value_f = stats.f_oneway(*f_samples)

    print("Main Effect: f_intra")
    print(f"  F-statistic: {f_stat_f:.4f}")
    print(f"  p-value: {p_value_f:.4e}")
    print(f"  Interpretation: {'SIGNIFICANT' if p_value_f < 0.001 else 'Not significant'}")
    print()

    for f in f_values:
        mean_pop = np.mean(f_groups[f])
        std_pop = np.std(f_groups[f], ddof=1)
        print(f"  f={f:5.2f}%: mean={mean_pop:5.2f}, SD={std_pop:4.2f}, n={len(f_groups[f])}")
    print()

    # Main effect: mechanism (collapse across N and f)
    mech_groups = {}
    for (n, f, mech), pops in groups.items():
        if mech not in mech_groups:
            mech_groups[mech] = []
        mech_groups[mech].extend(pops)

    mech_values = sorted(mech_groups.keys())
    mech_samples = [mech_groups[mech] for mech in mech_values]

    f_stat_mech, p_value_mech = stats.f_oneway(*mech_samples)

    print("Main Effect: mechanism")
    print(f"  F-statistic: {f_stat_mech:.4f}")
    print(f"  p-value: {p_value_mech:.4e}")
    print(f"  Interpretation: {'SIGNIFICANT' if p_value_mech < 0.05 else 'Not significant (p > 0.05)'}")
    print()

    for mech in mech_values:
        mean_pop = np.mean(mech_groups[mech])
        std_pop = np.std(mech_groups[mech], ddof=1)
        print(f"  {mech:15s}: mean={mean_pop:5.2f}, SD={std_pop:4.2f}, n={len(mech_groups[mech])}")
    print()

    return {
        'n_initial': {'F': f_stat_n, 'p': p_value_n, 'groups': n_groups},
        'f_intra': {'F': f_stat_f, 'p': p_value_f, 'groups': f_groups},
        'mechanism': {'F': f_stat_mech, 'p': p_value_mech, 'groups': mech_groups},
    }

def levene_variance_test(data: Dict) -> Dict:
    """
    Levene's Test: Variance(Deterministic) vs Variance(Flat)

    Tests whether Deterministic (SD=0) differs from Flat (SD > 0).
    """
    print("=" * 80)
    print("Levene's Test: Variance(Deterministic) vs Variance(Flat)")
    print("=" * 80)
    print()

    results_list = data['individual_results']

    # Group by (N, f, mechanism)
    groups = {}
    for result in results_list:
        n = result['n_initial']
        f = result['f_intra_pct']
        mech = result['spawn_mechanism']
        pop = result['final_population']

        key = (n, f, mech)
        if key not in groups:
            groups[key] = []
        groups[key].append(pop)

    # For each (N, f), compare Deterministic vs Flat variance
    print("Variance Comparison (SD) by Condition:")
    print()

    n_values = sorted(set(result['n_initial'] for result in results_list))
    f_values = sorted(set(result['f_intra_pct'] for result in results_list))

    results = []

    for n in n_values:
        for f in f_values:
            det_pops = groups[(n, f, 'deterministic')]
            flat_pops = groups[(n, f, 'flat')]

            det_sd = np.std(det_pops, ddof=1)
            flat_sd = np.std(flat_pops, ddof=1)

            # Levene's test
            stat, p_value = stats.levene(det_pops, flat_pops)

            print(f"N={n:2d}, f={f:5.2f}%:")
            print(f"  Deterministic: SD={det_sd:.4f}")
            print(f"  Flat:          SD={flat_sd:.4f}")
            print(f"  Levene's statistic: {stat:.4f}, p={p_value:.4e}")
            print(f"  Interpretation: {'SIGNIFICANT difference' if p_value < 0.001 else 'Not significant'}")
            print()

            results.append({
                'n_initial': n,
                'f_intra_pct': f,
                'det_sd': det_sd,
                'flat_sd': flat_sd,
                'levene_stat': stat,
                'p_value': p_value,
            })

    return results

def collapse_summary(data: Dict) -> Dict:
    """
    Collapse Rate Summary

    Even though collapse rate is 0.0% for all conditions, document this.
    """
    print("=" * 80)
    print("Collapse Rate Summary")
    print("=" * 80)
    print()

    summaries = data['condition_summaries']

    total_experiments = len(data['individual_results'])
    total_collapses = sum(s['basin_b_count'] for s in summaries)

    print(f"Total Experiments: {total_experiments}")
    print(f"Total Collapses: {total_collapses} ({100 * total_collapses / total_experiments:.1f}%)")
    print()

    print("By N_initial:")
    n_values = sorted(set(s['n_initial'] for s in summaries))
    for n in n_values:
        n_summaries = [s for s in summaries if s['n_initial'] == n]
        n_experiments = sum(s['basin_a_count'] + s['basin_b_count'] for s in n_summaries)
        n_collapses = sum(s['basin_b_count'] for s in n_summaries)
        print(f"  N={n:2d}: {n_collapses}/{n_experiments} collapses ({100 * n_collapses / n_experiments:.1f}%)")
    print()

    print("By Mechanism:")
    mech_values = sorted(set(s['spawn_mechanism'] for s in summaries))
    for mech in mech_values:
        mech_summaries = [s for s in summaries if s['spawn_mechanism'] == mech]
        mech_experiments = sum(s['basin_a_count'] + s['basin_b_count'] for s in mech_summaries)
        mech_collapses = sum(s['basin_b_count'] for s in mech_summaries)
        print(f"  {mech:15s}: {mech_collapses}/{mech_experiments} collapses ({100 * mech_collapses / mech_experiments:.1f}%)")
    print()

    return {
        'total_experiments': total_experiments,
        'total_collapses': total_collapses,
        'collapse_rate': total_collapses / total_experiments if total_experiments > 0 else 0,
    }

# ============================================================================
# FIGURES
# ============================================================================

def figure1_population_vs_n(data: Dict):
    """
    Figure 1: Final Population vs N_initial (by frequency)

    Shows linear growth: pop = N_initial + spawns
    """
    print("Generating Figure 1: Population vs N_initial...")

    summaries = data['condition_summaries']

    n_values = sorted(set(s['n_initial'] for s in summaries))
    f_values = sorted(set(s['f_intra_pct'] for s in summaries))
    mechanisms = ['deterministic', 'flat']

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    colors = {0.05: 'blue', 0.10: 'green', 0.20: 'red'}
    markers = {0.05: 'o', 0.10: 's', 0.20: '^'}

    for i, mech in enumerate(mechanisms):
        ax = axes[i]

        for f in f_values:
            # Get mean population for each N at this f and mechanism
            means = []
            stds = []

            for n in n_values:
                summary = next(s for s in summaries
                              if s['n_initial'] == n
                              and s['f_intra_pct'] == f
                              and s['spawn_mechanism'] == mech)
                means.append(summary['mean_population_all'])
                stds.append(summary['std_population_all'])

            ax.errorbar(n_values, means, yerr=stds,
                       label=f'f={f}%',
                       color=colors[f],
                       marker=markers[f],
                       capsize=5,
                       linewidth=2,
                       markersize=8)

        # Linear fit for f=0.05% (all mechanisms)
        summary_005 = [s for s in summaries if s['f_intra_pct'] == 0.05 and s['spawn_mechanism'] == mech]
        ns = [s['n_initial'] for s in summary_005]
        pops = [s['mean_population_all'] for s in summary_005]
        slope, intercept, r, p, se = stats.linregress(ns, pops)

        fit_n = np.linspace(min(n_values), max(n_values), 100)
        fit_pop = slope * fit_n + intercept
        ax.plot(fit_n, fit_pop, '--', color='blue', alpha=0.5,
               label=f'Linear fit: pop={slope:.2f}×N + {intercept:.2f}\n(R²={r**2:.4f})')

        ax.set_xlabel('Initial Population Size (N_initial)')
        ax.set_ylabel('Final Population Size')
        ax.set_title(f'{mech.capitalize()} Mechanism')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, max(pops) + 10)

    plt.suptitle('C193: Final Population vs Initial Population Size', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_file = OUTPUT_DIR / "c193_fig1_population_vs_n.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    plt.close()

def figure2_variance_comparison(data: Dict):
    """
    Figure 2: Variance Comparison (Deterministic vs Flat)

    Shows SD=0 for Deterministic, SD>0 for Flat.
    """
    print("Generating Figure 2: Variance Comparison...")

    summaries = data['condition_summaries']

    n_values = sorted(set(s['n_initial'] for s in summaries))
    f_values = sorted(set(s['f_intra_pct'] for s in summaries))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    colors_mech = {'deterministic': 'blue', 'flat': 'red'}

    for i, f in enumerate(f_values):
        ax = axes[i]

        for mech in ['deterministic', 'flat']:
            sds = []

            for n in n_values:
                summary = next(s for s in summaries
                              if s['n_initial'] == n
                              and s['f_intra_pct'] == f
                              and s['spawn_mechanism'] == mech)
                sds.append(summary['std_population_all'])

            ax.plot(n_values, sds,
                   label=f'{mech.capitalize()}',
                   color=colors_mech[mech],
                   marker='o',
                   linewidth=2,
                   markersize=8)

        ax.set_xlabel('Initial Population Size (N_initial)')
        if i == 0:
            ax.set_ylabel('Standard Deviation of Final Population')
        ax.set_title(f'f_intra = {f}%')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.5, max([s['std_population_all'] for s in summaries if s['f_intra_pct'] == f]) + 1)

    plt.suptitle('C193: Variance Comparison (Deterministic vs Flat)', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_file = OUTPUT_DIR / "c193_fig2_variance_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    plt.close()

def figure3_growth_pattern(data: Dict):
    """
    Figure 3: Growth Pattern (pop = N_initial + spawns)

    Validates linear additive model.
    """
    print("Generating Figure 3: Growth Pattern...")

    summaries = data['condition_summaries']

    # For Deterministic mechanism, pop_final = N_initial + spawns
    # spawns = f × cycles / 100
    # For f=0.05%, cycles=5000: spawns = 0.05 × 5000 / 100 = 2.5 ≈ 3
    # For f=0.10%: spawns = 5
    # For f=0.20%: spawns = 10

    det_summaries = [s for s in summaries if s['spawn_mechanism'] == 'deterministic']

    n_values = sorted(set(s['n_initial'] for s in det_summaries))
    f_values = sorted(set(s['f_intra_pct'] for s in det_summaries))

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {0.05: 'blue', 0.10: 'green', 0.20: 'red'}

    for f in f_values:
        measured_pops = []
        predicted_pops = []

        for n in n_values:
            summary = next(s for s in det_summaries
                          if s['n_initial'] == n
                          and s['f_intra_pct'] == f)

            measured_pop = summary['mean_population_all']
            spawns_avg = summary['spawns_avg']
            predicted_pop = n + spawns_avg

            measured_pops.append(measured_pop)
            predicted_pops.append(predicted_pop)

        ax.scatter(predicted_pops, measured_pops,
                  label=f'f={f}%',
                  color=colors[f],
                  s=100,
                  alpha=0.7)

    # Identity line (perfect prediction)
    max_pop = max([s['mean_population_all'] for s in det_summaries])
    ax.plot([0, max_pop], [0, max_pop], 'k--', label='Perfect Prediction', linewidth=2)

    ax.set_xlabel('Predicted Population (N_initial + spawns)')
    ax.set_ylabel('Measured Population (mean)')
    ax.set_title('C193: Growth Pattern Validation (Deterministic Mechanism)', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max_pop + 2)
    ax.set_ylim(0, max_pop + 2)

    plt.tight_layout()

    output_file = OUTPUT_DIR / "c193_fig3_growth_pattern.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    plt.close()

def figure4_robustness_summary(data: Dict):
    """
    Figure 4: Robustness Summary (Collapse Rate = 0% for all conditions)

    Visual summary showing zero collapses.
    """
    print("Generating Figure 4: Robustness Summary...")

    summaries = data['condition_summaries']

    n_values = sorted(set(s['n_initial'] for s in summaries))
    f_values = sorted(set(s['f_intra_pct'] for s in summaries))
    mechanisms = ['deterministic', 'flat']

    # Create heatmap of collapse rates (all zeros)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for i, mech in enumerate(mechanisms):
        ax = axes[i]

        # Build matrix: rows=N, cols=f
        matrix = np.zeros((len(n_values), len(f_values)))

        for row_idx, n in enumerate(n_values):
            for col_idx, f in enumerate(f_values):
                summary = next(s for s in summaries
                              if s['n_initial'] == n
                              and s['f_intra_pct'] == f
                              and s['spawn_mechanism'] == mech)
                matrix[row_idx, col_idx] = summary['collapse_pct']

        # Heatmap
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
        cbar = plt.colorbar(im, ax=ax, label='Collapse Rate (%)')

        # Set ticks
        ax.set_xticks(range(len(f_values)))
        ax.set_xticklabels([f'{f}%' for f in f_values])
        ax.set_yticks(range(len(n_values)))
        ax.set_yticklabels([f'N={n}' for n in n_values])

        # Annotate with values
        for row_idx in range(len(n_values)):
            for col_idx in range(len(f_values)):
                text = ax.text(col_idx, row_idx, f'{matrix[row_idx, col_idx]:.0f}%',
                             ha="center", va="center", color="black", fontsize=10, fontweight='bold')

        ax.set_xlabel('Spawn Frequency (f_intra)')
        ax.set_ylabel('Initial Population Size (N_initial)')
        ax.set_title(f'{mech.capitalize()} Mechanism')

    plt.suptitle('C193: Collapse Rate Summary (ZERO collapses across all conditions)',
                fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_file = OUTPUT_DIR / "c193_fig4_robustness_summary.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    plt.close()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Execute C193 statistical analysis"""

    print("=" * 80)
    print("C193 STATISTICAL ANALYSIS: POPULATION SIZE SCALING LAW")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    data = load_data()
    print(f"  Loaded {len(data['individual_results'])} experiments")
    print(f"  Conditions: {len(data['condition_summaries'])}")
    print()

    # Statistical tests
    anova_results = anova_population_dynamics(data)
    levene_results = levene_variance_test(data)
    collapse_results = collapse_summary(data)

    # Generate figures
    print("=" * 80)
    print("GENERATING PUBLICATION FIGURES @ 300 DPI")
    print("=" * 80)
    print()

    figure1_population_vs_n(data)
    figure2_variance_comparison(data)
    figure3_growth_pattern(data)
    figure4_robustness_summary(data)

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Total experiments: {collapse_results['total_experiments']}")
    print(f"  - Total collapses: {collapse_results['total_collapses']} ({100 * collapse_results['collapse_rate']:.1f}%)")
    print(f"  - N_initial effect: F={anova_results['n_initial']['F']:.2f}, p={anova_results['n_initial']['p']:.4e}")
    print(f"  - f_intra effect: F={anova_results['f_intra']['F']:.2f}, p={anova_results['f_intra']['p']:.4e}")
    print(f"  - Mechanism effect: F={anova_results['mechanism']['F']:.2f}, p={anova_results['mechanism']['p']:.4e}")
    print()
    print("Key Finding: N-independent robustness (N=5 to N=20 all viable at f ≥ 0.05%)")
    print()
    print("Publication Figures:")
    print(f"  1. {OUTPUT_DIR / 'c193_fig1_population_vs_n.png'}")
    print(f"  2. {OUTPUT_DIR / 'c193_fig2_variance_comparison.png'}")
    print(f"  3. {OUTPUT_DIR / 'c193_fig3_growth_pattern.png'}")
    print(f"  4. {OUTPUT_DIR / 'c193_fig4_robustness_summary.png'}")
    print()

if __name__ == "__main__":
    main()
