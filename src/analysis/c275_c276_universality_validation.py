#!/usr/bin/env python3
"""
C275/C276 Analysis: β Universality Validation
==============================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1475)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Purpose:
--------
Validate β ≈ 2.19 universality across different system configurations:
- C275: Energy parameter variation (3 conditions)
- C276: Topology variation (4 conditions)

Tests whether β is truly universal (invariant across configurations) or
configuration-dependent (varies with energy scale or topology).

Analysis Steps:
---------------
1. Load results from C275 (energy variation) and C276 (topology variation)
2. Fit power law E_min ∝ f^-β for each configuration
3. Extract β for each condition
4. Test universality: Is CV(β) < 15%? Is mean β = 2.19 ± 0.3?
5. Identify which factors affect β (if any)
6. Generate comparative visualization

Hypothesis Test:
----------------
**Null (H0):** β = 2.19 ± 0.3 across ALL configurations (universal)
**Alternative (H1):** β varies significantly across configurations

Outputs:
--------
1. Summary JSON with β values for each configuration
2. Figure 1: β universality across all configurations
3. Figure 2: Power law fits for each configuration
4. Figure 3: Configuration comparison (baseline vs. scaling)
"""

import json
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats as scipy_stats

# ============================================================================
# CONFIGURATION
# ============================================================================

# Input/Output directories
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
FIGURES_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Theoretical prediction
BETA_THEORY = 2.19
BETA_TOLERANCE = 0.3  # ±15%

# C275 configurations (energy variation)
C275_CONDITIONS = ["LOW_ENERGY", "MED_ENERGY", "HIGH_ENERGY"]
C275_FREQUENCIES = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]
C275_SEEDS = list(range(200, 210))

# C276 configurations (topology variation)
C276_CONDITIONS = ["FULLY_CONNECTED", "RING", "STAR", "RANDOM_GRAPH"]
C276_FREQUENCIES = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]
C276_SEEDS = list(range(300, 310))

# ============================================================================
# DATA LOADING
# ============================================================================

def load_c275_data(condition: str, freq: float, seed: int) -> Dict:
    """Load C275 experiment data (energy parameter variation)."""
    freq_pct = f"{freq * 100:.2f}".replace('.', '_')
    db_path = RESULTS_DIR / f"c275_UNIV_ENERGY_{condition}_f{freq_pct}pct_seed{seed}.db"

    if not db_path.exists():
        return {"error": "Database not found", "final_population": 0}

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT population FROM cycle_metrics ORDER BY cycle DESC LIMIT 1")
        result = cursor.fetchone()
        final_pop = result[0] if result else 0
        conn.close()

        return {"condition": condition, "frequency": freq, "seed": seed, "final_population": final_pop}

    except Exception as e:
        return {"error": str(e), "final_population": 0}


def load_c276_data(topology: str, freq: float, seed: int) -> Dict:
    """Load C276 experiment data (topology variation)."""
    freq_pct = f"{freq * 100:.2f}".replace('.', '_')
    db_path = RESULTS_DIR / f"c276_UNIV_TOPO_{topology}_f{freq_pct}pct_seed{seed}.db"

    if not db_path.exists():
        return {"error": "Database not found", "final_population": 0}

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT population FROM cycle_metrics ORDER BY cycle DESC LIMIT 1")
        result = cursor.fetchone()
        final_pop = result[0] if result else 0
        conn.close()

        return {"topology": topology, "frequency": freq, "seed": seed, "final_population": final_pop}

    except Exception as e:
        return {"error": str(e), "final_population": 0}


def load_all_data() -> Dict:
    """Load all C275 and C276 data."""
    print("Loading experimental data...")

    data = {"C275": {}, "C276": {}}

    # Load C275 (energy variation)
    for condition in C275_CONDITIONS:
        data["C275"][condition] = {}
        for freq in C275_FREQUENCIES:
            populations = []
            for seed in C275_SEEDS:
                result = load_c275_data(condition, freq, seed)
                if "error" not in result:
                    populations.append(result["final_population"])
            data["C275"][condition][freq] = populations

    # Load C276 (topology variation)
    for topology in C276_CONDITIONS:
        data["C276"][topology] = {}
        for freq in C276_FREQUENCIES:
            populations = []
            for seed in C276_SEEDS:
                result = load_c276_data(topology, freq, seed)
                if "error" not in result:
                    populations.append(result["final_population"])
            data["C276"][topology][freq] = populations

    print(f"✓ Loaded C275: {len(C275_CONDITIONS)} energy conditions")
    print(f"✓ Loaded C276: {len(C276_CONDITIONS)} topologies")

    return data


# ============================================================================
# POWER LAW FITTING
# ============================================================================

def fit_power_law(frequencies: np.ndarray, populations: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Fit power law: N(f) = E_∞ + A × f^-β

    Returns: (β, A, E_∞, R²)
    """
    # Estimate baseline
    E_inf_estimate = np.mean(populations[-2:])

    # Subtract baseline
    N_shifted = populations - E_inf_estimate

    # Filter positive values
    valid_mask = N_shifted > 0
    if valid_mask.sum() < 3:
        return np.nan, np.nan, E_inf_estimate, 0.0

    log_f = np.log10(frequencies[valid_mask])
    log_N = np.log10(N_shifted[valid_mask])

    # Linear regression
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(log_f, log_N)

    beta = -slope
    A = 10 ** intercept
    r_squared = r_value ** 2

    return beta, A, E_inf_estimate, r_squared


def fit_all_configurations(data: Dict) -> Dict:
    """Fit power law for all configurations."""
    print("\nFitting power laws for all configurations...")

    fits = {"C275": {}, "C276": {}}

    # Fit C275 (energy variation)
    for condition, freq_data in data["C275"].items():
        frequencies = np.array(sorted(freq_data.keys()))
        mean_pops = np.array([np.mean(freq_data[f]) for f in frequencies])

        beta, A, E_inf, r_squared = fit_power_law(frequencies, mean_pops)

        fits["C275"][condition] = {
            "beta": beta,
            "A": A,
            "E_inf": E_inf,
            "R2": r_squared,
            "frequencies": frequencies.tolist(),
            "mean_populations": mean_pops.tolist()
        }

        beta_status = "✓" if (BETA_THEORY - BETA_TOLERANCE) <= beta <= (BETA_THEORY + BETA_TOLERANCE) else "✗"
        print(f"C275 {condition}: β = {beta:.2f}, R² = {r_squared:.4f} {beta_status}")

    # Fit C276 (topology variation)
    for topology, freq_data in data["C276"].items():
        frequencies = np.array(sorted(freq_data.keys()))
        mean_pops = np.array([np.mean(freq_data[f]) for f in frequencies])

        beta, A, E_inf, r_squared = fit_power_law(frequencies, mean_pops)

        fits["C276"][topology] = {
            "beta": beta,
            "A": A,
            "E_inf": E_inf,
            "R2": r_squared,
            "frequencies": frequencies.tolist(),
            "mean_populations": mean_pops.tolist()
        }

        beta_status = "✓" if (BETA_THEORY - BETA_TOLERANCE) <= beta <= (BETA_THEORY + BETA_TOLERANCE) else "✗"
        print(f"C276 {topology}: β = {beta:.2f}, R² = {r_squared:.4f} {beta_status}")

    return fits


# ============================================================================
# UNIVERSALITY TEST
# ============================================================================

def test_universality(fits: Dict) -> Dict:
    """Test β universality across all configurations."""
    print("\nTesting β universality...")

    # Extract all β values
    beta_values = []
    labels = []

    for condition, fit_data in fits["C275"].items():
        beta_values.append(fit_data["beta"])
        labels.append(f"C275_{condition}")

    for topology, fit_data in fits["C276"].items():
        beta_values.append(fit_data["beta"])
        labels.append(f"C276_{topology}")

    beta_values = np.array(beta_values)
    mean_beta = np.mean(beta_values)
    std_beta = np.std(beta_values, ddof=1)
    cv_beta = std_beta / mean_beta if mean_beta > 0 else 0

    # Hypothesis test
    beta_min = BETA_THEORY - BETA_TOLERANCE
    beta_max = BETA_THEORY + BETA_TOLERANCE
    hypothesis_supported = (beta_min <= mean_beta <= beta_max) and (cv_beta < 0.15)

    result = {
        "beta_values": beta_values.tolist(),
        "labels": labels,
        "mean_beta": mean_beta,
        "std_beta": std_beta,
        "cv_beta": cv_beta,
        "beta_theory": BETA_THEORY,
        "hypothesis_supported": hypothesis_supported
    }

    print(f"Mean β = {mean_beta:.2f} ± {std_beta:.2f}")
    print(f"CV(β) = {cv_beta*100:.1f}%")
    print(f"Theory: β = {BETA_THEORY:.2f} ± {BETA_TOLERANCE:.2f}")
    print(f"Result: {'✓ HYPOTHESIS SUPPORTED' if hypothesis_supported else '✗ HYPOTHESIS NOT SUPPORTED'}")

    return result


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_universality_test(fits: Dict, universality_result: Dict):
    """Plot β values across all configurations."""
    print("\nGenerating universality plot...")

    beta_values = universality_result["beta_values"]
    labels = universality_result["labels"]
    mean_beta = universality_result["mean_beta"]
    beta_theory = universality_result["beta_theory"]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot β values
    x_pos = np.arange(len(beta_values))
    colors = ['blue']*len(fits["C275"]) + ['green']*len(fits["C276"])

    ax.bar(x_pos, beta_values, color=colors, alpha=0.7, edgecolor='black')

    # Plot mean and theory lines
    ax.axhline(y=mean_beta, color='red', linestyle='--', linewidth=2,
               label=f'Mean β = {mean_beta:.2f}')
    ax.axhline(y=beta_theory, color='black', linestyle='-', linewidth=2,
               label=f'Theory β = {beta_theory:.2f}')
    ax.axhspan(beta_theory - BETA_TOLERANCE, beta_theory + BETA_TOLERANCE,
               alpha=0.2, color='gray', label='±15% tolerance')

    ax.set_xlabel('Configuration', fontsize=12)
    ax.set_ylabel('Fitted Exponent β', fontsize=12)
    ax.set_title('β Universality Test: Energy Power Law Exponent Across Configurations',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    # Add divider
    ax.axvline(x=len(fits["C275"]) - 0.5, color='black', linestyle=':', linewidth=2)
    ax.text(len(fits["C275"]) / 2, ax.get_ylim()[1] * 0.95, 'C275\n(Energy)',
            ha='center', fontsize=10, fontweight='bold')
    ax.text(len(fits["C275"]) + len(fits["C276"]) / 2, ax.get_ylim()[1] * 0.95, 'C276\n(Topology)',
            ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c275_c276_universality_test.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: c275_c276_universality_test.png")
    plt.close()


def plot_power_law_fits(fits: Dict):
    """Plot power law fits for all configurations."""
    print("Generating power law fit plots...")

    n_configs = len(fits["C275"]) + len(fits["C276"])
    n_cols = 4
    n_rows = (n_configs + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, n_rows * 4))
    axes = axes.flatten() if n_configs > 1 else [axes]

    idx = 0

    # Plot C275
    for condition, fit_data in fits["C275"].items():
        ax = axes[idx]

        frequencies = np.array(fit_data["frequencies"])
        mean_pops = np.array(fit_data["mean_populations"])
        beta = fit_data["beta"]
        A = fit_data["A"]
        E_inf = fit_data["E_inf"]
        r_squared = fit_data["R2"]

        ax.plot(frequencies * 100, mean_pops, 'o', markersize=8, label='Data', color='blue')

        f_fit = np.logspace(np.log10(frequencies.min()), np.log10(frequencies.max()), 100)
        N_fit = E_inf + A / (f_fit ** beta)
        ax.plot(f_fit * 100, N_fit, '-', linewidth=2, color='red',
                label=f'β = {beta:.2f} (R² = {r_squared:.3f})')

        ax.set_xlabel('Frequency (%)', fontsize=10)
        ax.set_ylabel('Mean Population', fontsize=10)
        ax.set_title(f'C275: {condition}', fontsize=11, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

        idx += 1

    # Plot C276
    for topology, fit_data in fits["C276"].items():
        ax = axes[idx]

        frequencies = np.array(fit_data["frequencies"])
        mean_pops = np.array(fit_data["mean_populations"])
        beta = fit_data["beta"]
        A = fit_data["A"]
        E_inf = fit_data["E_inf"]
        r_squared = fit_data["R2"]

        ax.plot(frequencies * 100, mean_pops, 'o', markersize=8, label='Data', color='green')

        f_fit = np.logspace(np.log10(frequencies.min()), np.log10(frequencies.max()), 100)
        N_fit = E_inf + A / (f_fit ** beta)
        ax.plot(f_fit * 100, N_fit, '-', linewidth=2, color='red',
                label=f'β = {beta:.2f} (R² = {r_squared:.3f})')

        ax.set_xlabel('Frequency (%)', fontsize=10)
        ax.set_ylabel('Mean Population', fontsize=10)
        ax.set_title(f'C276: {topology}', fontsize=11, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

        idx += 1

    # Hide unused subplots
    for idx in range(n_configs, len(axes)):
        axes[idx].axis('off')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c275_c276_power_law_fits.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: c275_c276_power_law_fits.png")
    plt.close()


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_universality():
    """Complete universality analysis for C275 and C276."""
    print("="*80)
    print("C275/C276 ANALYSIS: β UNIVERSALITY VALIDATION")
    print("="*80)

    # Load data
    data = load_all_data()

    # Fit power laws
    fits = fit_all_configurations(data)

    # Test universality
    universality_result = test_universality(fits)

    # Visualizations
    plot_universality_test(fits, universality_result)
    plot_power_law_fits(fits)

    # Save summary
    summary = {
        "power_law_fits": fits,
        "universality_test": universality_result
    }

    summary_file = RESULTS_DIR / "c275_c276_universality_analysis_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"Summary saved: {summary_file}")
    print(f"Figures saved: {FIGURES_DIR}")


if __name__ == "__main__":
    analyze_universality()
