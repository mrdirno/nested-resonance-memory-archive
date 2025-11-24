#!/usr/bin/env python3
"""
C186 V6 Results Analysis: Ultra-Low Frequency Test
===================================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1073)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Analyze C186 V6 ultra-low frequency test results to determine:
1. Actual f_hier_crit (hierarchical critical frequency)
2. Precise bounds on hierarchical scaling coefficient α
3. Where linear model breaks down
4. Basin transition behavior at extreme low frequencies

Background:
-----------
C186 V1-V5 Results (all Basin A):
- f=5.0%: mean_pop=170.0
- f=2.5%: mean_pop=95.0
- f=2.0%: mean_pop=79.9
- f=1.5%: mean_pop=64.9
- f=1.0%: mean_pop=49.8

Linear Regression (R² = 1.000):
Population = 30.04 × Frequency + 19.80

This model predicts viability at all frequencies > 0% (population always >2.5).

C186 V6 Tests:
- f=0.75%: Linear predicts 42.3 agents
- f=0.50%: Linear predicts 34.8 agents
- f=0.25%: Linear predicts 27.3 agents
- f=0.10%: Linear predicts 22.8 agents

All above Basin A threshold (2.5), but spawn intervals become extreme:
- f=0.75% → spawn every 133 cycles
- f=0.50% → spawn every 200 cycles
- f=0.25% → spawn every 400 cycles
- f=0.10% → spawn every 1000 cycles

Hypothesis: System will collapse when spawn interval exceeds population resilience,
despite linear model prediction.

Analysis Tasks:
---------------
1. Load V6 results and extract statistics
2. Compare observed vs predicted (linear model)
3. Identify Basin A/B distribution
4. Calculate f_hier_crit (if collapse observed)
5. Calculate precise α bounds
6. Generate V6-specific figures
7. Integrate with V1-V5 results for comprehensive visualization
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any
from scipy import stats as scipy_stats

# ============================================================================
# CONFIGURATION
# ============================================================================

RESULTS_FILE = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v6_ultra_low_frequency_test.json")
FIGURES_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Linear model from V1-V5
LINEAR_SLOPE = 30.04
LINEAR_INTERCEPT = 19.80

# Basin classification
BASIN_A_THRESHOLD = 2.5

# C177 V2 baseline
F_SINGLE_CRIT = 6.25  # % (from C177 V2 analysis)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_v6_results() -> Dict[str, Any]:
    """Load C186 V6 results JSON."""
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"V6 results not found: {RESULTS_FILE}")

    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)

def load_v1_v5_results() -> Dict[str, Any]:
    """Load combined V1-V5 results for comparison."""
    results_files = [
        Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v1_hierarchical_spawn_failure.json"),
        Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v2_hierarchical_spawn_success.json"),
        Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v3_low_frequency_test.json"),
        Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v4_low_frequency_test.json"),
        Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v5_ultra_low_frequency_test.json")
    ]

    all_experiments = []
    for rf in results_files:
        if rf.exists():
            with open(rf, 'r') as f:
                data = json.load(f)
                if "experiments" in data:
                    all_experiments.extend(data["experiments"])

    return {"experiments": all_experiments}

# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def extract_v6_statistics(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract statistics from V6 results."""
    stats = []

    for exp in results["experiments"]:
        f_intra = exp["f_intra"]
        f_intra_pct = exp["f_intra_pct"]

        individual_runs = exp["individual_runs"]
        agg_stats = exp["aggregate_statistics"]

        # Linear model prediction
        predicted_pop = LINEAR_SLOPE * f_intra_pct + LINEAR_INTERCEPT

        # Observed
        observed_pop = agg_stats["mean_population_avg"]
        pop_std = agg_stats["mean_population_std"]

        # Basin classification
        basin_a_pct = agg_stats["basin_a_pct"]

        # Spawn interval
        spawn_interval = exp["spawn_interval"]

        stats.append({
            "f_intra_pct": f_intra_pct,
            "spawn_interval": spawn_interval,
            "predicted_population": predicted_pop,
            "observed_population": observed_pop,
            "population_std": pop_std,
            "basin_a_pct": basin_a_pct,
            "n_runs": len(individual_runs)
        })

    return sorted(stats, key=lambda x: x["f_intra_pct"])

def calculate_f_hier_crit(stats: List[Dict[str, Any]]) -> float:
    """Calculate hierarchical critical frequency (50% Basin A threshold)."""
    # Find frequency where Basin A % crosses 50%
    for i in range(len(stats) - 1):
        if stats[i]["basin_a_pct"] < 50 and stats[i+1]["basin_a_pct"] >= 50:
            # Linear interpolation
            f1, p1 = stats[i]["f_intra_pct"], stats[i]["basin_a_pct"]
            f2, p2 = stats[i+1]["f_intra_pct"], stats[i+1]["basin_a_pct"]
            f_crit = f1 + (50 - p1) * (f2 - f1) / (p2 - p1)
            return f_crit

    # If all Basin A, f_crit < min(f_tested)
    if all(s["basin_a_pct"] >= 50 for s in stats):
        return stats[0]["f_intra_pct"]  # Lower bound

    # If all Basin B, f_crit > max(f_tested)
    if all(s["basin_a_pct"] < 50 for s in stats):
        return stats[-1]["f_intra_pct"]  # Upper bound

    return None

def calculate_alpha_bounds(f_hier_crit: float) -> Dict[str, float]:
    """Calculate hierarchical scaling coefficient bounds."""
    alpha = f_hier_crit / F_SINGLE_CRIT

    return {
        "f_hier_crit": f_hier_crit,
        "f_single_crit": F_SINGLE_CRIT,
        "alpha": alpha,
        "interpretation": "hierarchical needs {:.1f}× spawn frequency of single-scale".format(alpha)
    }

# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_v6_observed_vs_predicted(stats: List[Dict[str, Any]]):
    """Figure 1: Observed vs predicted population (linear model)."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    frequencies = [s["f_intra_pct"] for s in stats]
    predicted = [s["predicted_population"] for s in stats]
    observed = [s["observed_population"] for s in stats]
    errors = [s["population_std"] for s in stats]

    # Plot predicted (linear model)
    ax.plot(frequencies, predicted, 'k--', linewidth=2, label='Linear Model Prediction', zorder=1)

    # Plot observed with error bars
    ax.errorbar(frequencies, observed, yerr=errors, fmt='o',
                color='#2E86AB', markersize=8, capsize=5, capthick=2,
                label='Observed (mean ± std)', zorder=2)

    # Basin A threshold
    ax.axhline(y=BASIN_A_THRESHOLD, color='red', linestyle=':', linewidth=2,
               label=f'Basin A Threshold ({BASIN_A_THRESHOLD})', zorder=0)

    ax.set_xlabel('Intra-Population Spawn Frequency (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Population', fontsize=12, fontweight='bold')
    ax.set_title('C186 V6: Observed vs Linear Model Prediction\n(Ultra-Low Frequency Test)',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c186_v6_observed_vs_predicted.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Figure 1: Observed vs Predicted saved")

def plot_v6_basin_distribution(stats: List[Dict[str, Any]]):
    """Figure 2: Basin A/B distribution across ultra-low frequencies."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    frequencies = [s["f_intra_pct"] for s in stats]
    basin_a_pcts = [s["basin_a_pct"] for s in stats]

    # Bar chart
    bars = ax.bar(frequencies, basin_a_pcts, width=0.15, color='#06A77D',
                   edgecolor='black', linewidth=1.5, label='Basin A %')

    # 50% threshold line
    ax.axhline(y=50, color='red', linestyle='--', linewidth=2, label='50% Threshold')

    # Annotate bars with percentages
    for bar, pct in zip(bars, basin_a_pcts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 2,
                f'{pct:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xlabel('Intra-Population Spawn Frequency (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Basin A Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_title('C186 V6: Basin Classification Distribution\n(Ultra-Low Frequency Test)',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c186_v6_basin_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Figure 2: Basin Distribution saved")

def plot_v6_spawn_interval_effect(stats: List[Dict[str, Any]]):
    """Figure 3: Effect of spawn interval on system viability."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    frequencies = [s["f_intra_pct"] for s in stats]
    spawn_intervals = [s["spawn_interval"] for s in stats]
    observed_pops = [s["observed_population"] for s in stats]
    basin_a_pcts = [s["basin_a_pct"] for s in stats]

    # Left panel: Spawn interval vs population
    ax1.scatter(spawn_intervals, observed_pops, s=100, color='#2E86AB',
                edgecolor='black', linewidth=1.5, zorder=2)
    ax1.axhline(y=BASIN_A_THRESHOLD, color='red', linestyle=':', linewidth=2,
                label=f'Basin A Threshold ({BASIN_A_THRESHOLD})', zorder=1)
    ax1.set_xlabel('Spawn Interval (cycles)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Mean Population', fontsize=12, fontweight='bold')
    ax1.set_title('Population vs Spawn Interval', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Right panel: Spawn interval vs Basin A %
    ax2.scatter(spawn_intervals, basin_a_pcts, s=100, color='#06A77D',
                edgecolor='black', linewidth=1.5, zorder=2)
    ax2.axhline(y=50, color='red', linestyle='--', linewidth=2,
                label='50% Threshold', zorder=1)
    ax2.set_xlabel('Spawn Interval (cycles)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Basin A Percentage (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Viability vs Spawn Interval', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c186_v6_spawn_interval_effect.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Figure 3: Spawn Interval Effect saved")

def plot_comprehensive_v1_v6_overview(v1_v5_stats: List[Dict[str, Any]], v6_stats: List[Dict[str, Any]]):
    """Figure 4: Comprehensive V1-V6 overview showing full frequency range."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=300)

    # Combine all data
    all_freqs = []
    all_pops = []
    all_errs = []
    all_basins = []

    # V1-V5 data
    for s in v1_v5_stats:
        all_freqs.append(s["f_intra_pct"])
        all_pops.append(s["observed_population"])
        all_errs.append(s["population_std"])
        all_basins.append(s["basin_a_pct"])

    # V6 data
    for s in v6_stats:
        all_freqs.append(s["f_intra_pct"])
        all_pops.append(s["observed_population"])
        all_errs.append(s["population_std"])
        all_basins.append(s["basin_a_pct"])

    # Sort by frequency
    sorted_data = sorted(zip(all_freqs, all_pops, all_errs, all_basins))
    all_freqs, all_pops, all_errs, all_basins = zip(*sorted_data)

    # Left panel: Population vs frequency (full range)
    ax1.errorbar(all_freqs, all_pops, yerr=all_errs, fmt='o',
                 color='#2E86AB', markersize=6, capsize=4, capthick=1.5,
                 label='Hierarchical System', zorder=2)

    # Linear model fit
    freq_range = np.linspace(min(all_freqs), max(all_freqs), 100)
    linear_pred = LINEAR_SLOPE * freq_range + LINEAR_INTERCEPT
    ax1.plot(freq_range, linear_pred, 'k--', linewidth=2,
             label=f'Linear Fit (R²=1.000)', zorder=1)

    ax1.axhline(y=BASIN_A_THRESHOLD, color='red', linestyle=':', linewidth=2,
                label=f'Basin A Threshold', zorder=0)
    ax1.set_xlabel('Intra-Population Spawn Frequency (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Mean Population', fontsize=12, fontweight='bold')
    ax1.set_title('Population Scaling (V1-V6 Combined)', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Right panel: Basin viability across full range
    colors = ['#06A77D' if b >= 50 else '#D90368' for b in all_basins]
    ax2.bar(all_freqs, all_basins, color=colors, edgecolor='black', linewidth=1.2)
    ax2.axhline(y=50, color='red', linestyle='--', linewidth=2, label='50% Threshold')
    ax2.set_xlabel('Intra-Population Spawn Frequency (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Basin A Percentage (%)', fontsize=12, fontweight='bold')
    ax2.set_title('System Viability (V1-V6 Combined)', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 110)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c186_v1_v6_comprehensive_overview.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Figure 4: Comprehensive V1-V6 Overview saved")

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    """Execute V6 analysis."""
    print("=" * 80)
    print("C186 V6 RESULTS ANALYSIS: ULTRA-LOW FREQUENCY TEST")
    print("=" * 80)
    print()

    # Load data
    print("Loading V6 results...")
    v6_results = load_v6_results()
    v6_stats = extract_v6_statistics(v6_results)

    print("Loading V1-V5 results for comparison...")
    v1_v5_results = load_v1_v5_results()
    v1_v5_stats = []

    # Extract V1-V5 statistics (similar format)
    for exp in v1_v5_results["experiments"]:
        if "aggregate_statistics" in exp:
            agg = exp["aggregate_statistics"]
            f_pct = exp.get("f_intra_pct", exp.get("spawn_frequency_pct", 0))

            predicted_pop = LINEAR_SLOPE * f_pct + LINEAR_INTERCEPT

            v1_v5_stats.append({
                "f_intra_pct": f_pct,
                "spawn_interval": exp.get("spawn_interval", int(100.0 / f_pct) if f_pct > 0 else 0),
                "predicted_population": predicted_pop,
                "observed_population": agg.get("mean_population_avg", 0),
                "population_std": agg.get("mean_population_std", 0),
                "basin_a_pct": agg.get("basin_a_pct", 0),
                "n_runs": 10
            })

    v1_v5_stats = sorted(v1_v5_stats, key=lambda x: x["f_intra_pct"])

    print(f"✓ Loaded {len(v6_stats)} V6 frequency conditions")
    print(f"✓ Loaded {len(v1_v5_stats)} V1-V5 frequency conditions")
    print()

    # Display V6 results
    print("V6 RESULTS SUMMARY:")
    print()
    print("Frequency | Interval | Predicted | Observed  | Basin A | Outcome")
    print("-" * 70)
    for s in v6_stats:
        outcome = "VIABLE" if s["basin_a_pct"] >= 50 else "COLLAPSE"
        print(f"{s['f_intra_pct']:7.2f}%  | {s['spawn_interval']:4d} cyc | "
              f"{s['predicted_population']:7.1f}   | {s['observed_population']:5.1f} ± {s['population_std']:4.1f} | "
              f"{s['basin_a_pct']:5.0f}%  | {outcome}")
    print()

    # Calculate f_hier_crit
    print("HIERARCHICAL CRITICAL FREQUENCY ANALYSIS:")
    print()

    # Combine V6 + V1-V5 for complete picture
    all_stats = v1_v5_stats + v6_stats
    all_stats = sorted(all_stats, key=lambda x: x["f_intra_pct"])

    f_hier_crit = calculate_f_hier_crit(all_stats)

    if f_hier_crit is not None:
        print(f"f_hier_crit ≈ {f_hier_crit:.2f}%")

        alpha_data = calculate_alpha_bounds(f_hier_crit)
        print(f"f_single_crit = {alpha_data['f_single_crit']:.2f}%")
        print(f"α = f_hier_crit / f_single_crit = {alpha_data['alpha']:.3f}")
        print(f"Interpretation: {alpha_data['interpretation']}")
    else:
        # Determine bounds
        basin_a_freqs = [s["f_intra_pct"] for s in all_stats if s["basin_a_pct"] >= 50]
        basin_b_freqs = [s["f_intra_pct"] for s in all_stats if s["basin_a_pct"] < 50]

        if len(basin_a_freqs) > 0 and len(basin_b_freqs) == 0:
            print(f"f_hier_crit < {min(basin_a_freqs):.2f}% (all tested frequencies viable)")
            print(f"α < {min(basin_a_freqs) / F_SINGLE_CRIT:.3f}")
        elif len(basin_b_freqs) > 0 and len(basin_a_freqs) == 0:
            print(f"f_hier_crit > {max(basin_b_freqs):.2f}% (all tested frequencies collapse)")
            print(f"α > {max(basin_b_freqs) / F_SINGLE_CRIT:.3f}")
        else:
            print("Unable to determine f_hier_crit (unexpected Basin distribution)")

    print()

    # Linear model breakdown analysis
    print("LINEAR MODEL BREAKDOWN ANALYSIS:")
    print()
    print("Linear Model: Population = 30.04 × Frequency + 19.80")
    print()

    for s in v6_stats:
        deviation = s["observed_population"] - s["predicted_population"]
        deviation_pct = (deviation / s["predicted_population"]) * 100
        print(f"f={s['f_intra_pct']:.2f}%: Predicted={s['predicted_population']:.1f}, "
              f"Observed={s['observed_population']:.1f}, "
              f"Deviation={deviation:+.1f} ({deviation_pct:+.1f}%)")

    print()

    # Generate figures
    print("Generating V6 analysis figures...")
    print()

    plot_v6_observed_vs_predicted(v6_stats)
    plot_v6_basin_distribution(v6_stats)
    plot_v6_spawn_interval_effect(v6_stats)
    plot_comprehensive_v1_v6_overview(v1_v5_stats, v6_stats)

    print()
    print("=" * 80)
    print("V6 ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Figures saved to: {FIGURES_DIR}")
    print()

    # Save analysis summary
    summary = {
        "v6_statistics": v6_stats,
        "v1_v5_statistics": v1_v5_stats,
        "f_hier_crit": f_hier_crit,
        "alpha_data": alpha_data if f_hier_crit is not None else None,
        "linear_model": {
            "slope": LINEAR_SLOPE,
            "intercept": LINEAR_INTERCEPT,
            "r_squared": 1.000
        }
    }

    summary_file = Path("/Volumes/dual/DUALITY-ZERO-V2/analysis/c186_v6_analysis_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Analysis summary saved to: {summary_file}")
    print()

if __name__ == "__main__":
    main()
