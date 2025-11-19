#!/usr/bin/env python3
"""
V6 Regime Boundary Dynamics Analysis
=====================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1470)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Analyze variance patterns across V6 three-regime framework to test hypothesis:
"Variance increases near regime boundaries as systems approach phase transitions"

Background:
-----------
V6 Three-Regime Validation (150 experiments):
- V6a (net = 0): Homeostasis at K ≈ 201 (0% collapse)
- V6b (net = +0.5): Growth to K ≈ 19,320 (0% collapse, σ = 1,102)
- V6c (net = -0.5): Collapse to 0 (100% collapse, σ = 0)

Observations:
- V6b shows HIGH variance (σ = 1,102 across 50 experiments)
- V6c shows ZERO variance (all exactly 0)
- V6a variance unknown (needs analysis)

Hypothesis:
-----------
Variance pattern should reveal proximity to regime boundaries:
- V6c (deep collapse): Zero variance (deterministic extinction)
- V6a (boundary regime): Low-moderate variance (near net = 0 transition)
- V6b (growth regime): High variance? (complex dynamics at high density)

Alternative: V6b high variance may indicate metastability or saturation effects,
not boundary proximity.

Analysis Tasks:
---------------
1. Load all V6 experiment results (a, b, c)
2. Calculate population variance across spawn rates for each regime
3. Test spawn-rate-dependent variance (does variance change with f?)
4. Compare energy variance across regimes
5. Look for variance signatures of regime transitions
6. Test coefficient of variation (CV = σ/μ) for scale-independent comparison

Expected Outcomes:
------------------
IF hypothesis correct:
- V6a (homeostasis, near boundary): Moderate CV
- V6b (growth, away from boundary): Low CV (stable growth)
- V6c (collapse, deterministic): Zero CV

IF alternative (saturation effects):
- V6b high variance due to carrying capacity constraints
- V6a low variance (simple equilibrium)
- V6c zero variance (deterministic)
"""

import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats as scipy_stats
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================

EXPERIMENTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
FIGURES_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# V6 regime parameters
V6_REGIMES = {
    'v6a': {'name': 'Homeostasis', 'net_energy': 0.0, 'E_consume': 1.0, 'E_recharge': 1.0},
    'v6b': {'name': 'Growth', 'net_energy': +0.5, 'E_consume': 0.5, 'E_recharge': 1.0},
    'v6c': {'name': 'Collapse', 'net_energy': -0.5, 'E_consume': 1.5, 'E_recharge': 1.0},
}

SPAWN_RATES = [0.001, 0.0025, 0.005, 0.0075, 0.01]
SEEDS = list(range(42, 52))  # 42-51

# ============================================================================
# DATA LOADING
# ============================================================================

def load_experiment_final_pop(regime: str, f_spawn: float, seed: int) -> int:
    """
    Load final population from experiment database.

    Returns:
        Final population count (0 if collapsed)
    """
    spawn_pct = f"{f_spawn * 100:.2f}".rstrip('0').rstrip('.')
    db_file = EXPERIMENTS_DIR / f"c186_{regime}_HIERARCHICAL_{spawn_pct}pct_seed{seed}.db"

    if not db_file.exists():
        print(f"Warning: DB not found: {db_file}")
        return 0

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get final population count
        cursor.execute("""
            SELECT COUNT(*) FROM agents
            WHERE status = 'active'
        """)

        final_pop = cursor.fetchone()[0]
        conn.close()

        return final_pop

    except Exception as e:
        print(f"Error loading {db_file}: {e}")
        return 0


def load_regime_data(regime: str) -> Dict[float, List[int]]:
    """
    Load all experiment results for a regime.

    Returns:
        Dict mapping spawn_rate -> list of final populations (one per seed)
    """
    regime_data = {f: [] for f in SPAWN_RATES}

    print(f"\nLoading {regime.upper()} regime data...")
    for f_spawn in SPAWN_RATES:
        for seed in SEEDS:
            final_pop = load_experiment_final_pop(regime, f_spawn, seed)
            regime_data[f_spawn].append(final_pop)

        n = len(regime_data[f_spawn])
        mean_pop = np.mean(regime_data[f_spawn])
        std_pop = np.std(regime_data[f_spawn], ddof=1)

        print(f"  f={f_spawn*100:.2f}%: n={n}, μ={mean_pop:.1f}, σ={std_pop:.1f}")

    return regime_data


def load_all_v6_data() -> Dict[str, Dict[float, List[int]]]:
    """Load data for all three V6 regimes."""
    return {
        regime: load_regime_data(regime)
        for regime in V6_REGIMES.keys()
    }


# ============================================================================
# VARIANCE ANALYSIS
# ============================================================================

def calculate_regime_statistics(regime_data: Dict[float, List[int]]) -> Dict[str, float]:
    """
    Calculate aggregate statistics across all spawn rates for a regime.

    Returns:
        Dict with mean, std, cv, min, max across ALL experiments in regime
    """
    all_pops = []
    for f_spawn in SPAWN_RATES:
        all_pops.extend(regime_data[f_spawn])

    all_pops = np.array(all_pops)

    mean_pop = np.mean(all_pops)
    std_pop = np.std(all_pops, ddof=1)
    cv = (std_pop / mean_pop) if mean_pop > 0 else 0.0

    return {
        'mean': mean_pop,
        'std': std_pop,
        'cv': cv,
        'min': np.min(all_pops),
        'max': np.max(all_pops),
        'n': len(all_pops),
    }


def test_spawn_rate_effect_on_variance(regime_data: Dict[float, List[int]]) -> Dict:
    """
    Test if variance changes significantly across spawn rates within a regime.

    Uses Levene's test for homogeneity of variances.
    """
    samples = [regime_data[f] for f in SPAWN_RATES]

    # Levene's test (tests H0: all groups have equal variance)
    statistic, p_value = scipy_stats.levene(*samples)

    # Calculate variance for each spawn rate
    variances = {f: np.var(regime_data[f], ddof=1) for f in SPAWN_RATES}

    return {
        'test': 'Levene',
        'statistic': statistic,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'variances_by_spawn': variances,
    }


# ============================================================================
# REGIME BOUNDARY ANALYSIS
# ============================================================================

def analyze_regime_boundaries(v6_data: Dict[str, Dict[float, List[int]]]):
    """
    Comprehensive analysis of variance patterns across regime boundaries.
    """
    print("\n" + "="*80)
    print("V6 REGIME BOUNDARY DYNAMICS ANALYSIS")
    print("="*80)

    # Calculate statistics for each regime
    regime_stats = {}
    for regime, data in v6_data.items():
        stats = calculate_regime_statistics(data)
        regime_stats[regime] = stats

        regime_name = V6_REGIMES[regime]['name']
        net_energy = V6_REGIMES[regime]['net_energy']

        print(f"\n{regime.upper()} ({regime_name}, net energy = {net_energy:+.1f}):")
        print(f"  Mean population: {stats['mean']:.1f} ± {stats['std']:.1f}")
        print(f"  Coefficient of variation: {stats['cv']:.4f}")
        print(f"  Range: [{stats['min']}, {stats['max']}]")
        print(f"  N = {stats['n']} experiments")

    # Test spawn-rate-dependent variance
    print("\n" + "-"*80)
    print("SPAWN RATE EFFECT ON VARIANCE (within each regime):")
    print("-"*80)

    for regime, data in v6_data.items():
        variance_test = test_spawn_rate_effect_on_variance(data)
        regime_name = V6_REGIMES[regime]['name']

        print(f"\n{regime.upper()} ({regime_name}):")
        print(f"  Levene statistic: {variance_test['statistic']:.4f}")
        print(f"  p-value: {variance_test['p_value']:.6f}")
        print(f"  Significant: {variance_test['significant']}")

        print(f"  Variances by spawn rate:")
        for f, var in variance_test['variances_by_spawn'].items():
            print(f"    f={f*100:.2f}%: σ² = {var:.2f}")

    # Cross-regime comparison
    print("\n" + "="*80)
    print("CROSS-REGIME COMPARISON:")
    print("="*80)

    print(f"\nCoefficient of Variation (CV = σ/μ):")
    print(f"  V6c (Collapse):   CV = {regime_stats['v6c']['cv']:.6f} (deterministic)")
    print(f"  V6a (Homeostasis): CV = {regime_stats['v6a']['cv']:.6f}")
    print(f"  V6b (Growth):      CV = {regime_stats['v6b']['cv']:.6f}")

    print(f"\nAbsolute Standard Deviation:")
    print(f"  V6c (Collapse):   σ = {regime_stats['v6c']['std']:.2f}")
    print(f"  V6a (Homeostasis): σ = {regime_stats['v6a']['std']:.2f}")
    print(f"  V6b (Growth):      σ = {regime_stats['v6b']['std']:.2f}")

    # Interpretation
    print("\n" + "="*80)
    print("INTERPRETATION:")
    print("="*80)

    if regime_stats['v6a']['cv'] > regime_stats['v6b']['cv']:
        print("\n✓ BOUNDARY HYPOTHESIS SUPPORTED:")
        print("  V6a (homeostasis, near net=0 boundary) has HIGHER CV than V6b (growth)")
        print("  This suggests increased variance near regime boundaries.")
    else:
        print("\n✗ BOUNDARY HYPOTHESIS NOT SUPPORTED:")
        print("  V6b (growth) has higher CV than V6a (homeostasis)")
        print("  High variance likely due to saturation/carrying capacity effects")

    if regime_stats['v6c']['std'] == 0:
        print("\n✓ COLLAPSE DETERMINISM CONFIRMED:")
        print("  V6c has exactly zero variance (100% deterministic collapse)")

    return regime_stats


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_variance_by_regime(v6_data: Dict[str, Dict[float, List[int]]], regime_stats: Dict):
    """
    Generate publication-quality figure showing variance patterns across regimes.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)

    for idx, (regime, data) in enumerate(v6_data.items()):
        ax = axes[idx]
        regime_name = V6_REGIMES[regime]['name']
        net_energy = V6_REGIMES[regime]['net_energy']

        # Collect data for box plot
        plot_data = [data[f] for f in SPAWN_RATES]
        spawn_labels = [f"{f*100:.2f}%" for f in SPAWN_RATES]

        # Box plot
        bp = ax.boxplot(plot_data, labels=spawn_labels, patch_artist=True)

        # Style
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue' if regime == 'v6a' else
                              'lightgreen' if regime == 'v6b' else 'salmon')

        ax.set_xlabel('Spawn Frequency', fontsize=12)
        ax.set_ylabel('Final Population', fontsize=12)
        ax.set_title(f"{regime_name} (E_net = {net_energy:+.1f})\n"
                    f"CV = {regime_stats[regime]['cv']:.4f}",
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = FIGURES_DIR / "v6_regime_boundary_variance_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Figure saved: {output_file}")

    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main analysis execution."""
    print("="*80)
    print("V6 REGIME BOUNDARY DYNAMICS ANALYSIS - CYCLE 1470")
    print("="*80)

    # Load data
    v6_data = load_all_v6_data()

    # Analyze
    regime_stats = analyze_regime_boundaries(v6_data)

    # Visualize
    plot_variance_by_regime(v6_data, regime_stats)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

    return regime_stats


if __name__ == "__main__":
    stats = main()
