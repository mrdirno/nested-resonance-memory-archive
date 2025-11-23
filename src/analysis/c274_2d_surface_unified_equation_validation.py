#!/usr/bin/env python3
"""
C274 Analysis: 2D Energy-Frequency Surface and Unified Equation Validation
===========================================================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1474)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Purpose:
--------
Validate unified scaling equation across complete energy-frequency parameter space:

E_min^hier(f, E_net) = {
    ∞                              if E_net < 0
    E_∞(E_net) + A(E_net)/(αf)^β  if E_net ≥ 0
}

Analysis Steps:
---------------
1. Load experimental results from 480 experiments
2. Calculate mean populations for each (E_net, f) condition
3. Identify regime boundaries (collapse vs. viable)
4. Fit power law E_min ∝ f^-β for each E_net ≥ 0 condition
5. Extract baseline E_∞(E_net) and amplitude A(E_net)
6. Test β universality (same exponent across all E_net ≥ 0?)
7. Visualize 2D surface and phase boundary
8. Generate publication-quality figures

Hypothesis Tests:
-----------------
1. **Sharp Boundary:** 100% collapse for ALL E_net < 0, 0% for E_net ≥ 0
2. **Universal β:** Same exponent (2.19 ± 0.3) for ALL E_net ≥ 0 conditions
3. **Baseline Scaling:** E_∞(E_net) varies systematically with net energy
4. **Phase Transition:** Abrupt change at E_net = 0

Outputs:
--------
1. Summary JSON with fitted parameters for each E_net condition
2. Figure 1: 2D surface plot (E_net, f) → N_final
3. Figure 2: Power law fits for each E_net ≥ 0 condition
4. Figure 3: β universality test (exponent vs. E_net)
5. Figure 4: Baseline and amplitude scaling (E_∞, A vs. E_net)
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

# Experimental parameters (must match C274 experiment)
ENERGY_CONDITIONS = [
    {"label": "E_net_minus0.2", "net": -0.2, "regime": "COLLAPSE"},
    {"label": "E_net_minus0.1", "net": -0.1, "regime": "COLLAPSE"},
    {"label": "E_net_0.0", "net": 0.0, "regime": "HOMEOSTASIS"},
    {"label": "E_net_plus0.1", "net": +0.1, "regime": "GROWTH"},
    {"label": "E_net_plus0.2", "net": +0.2, "regime": "GROWTH"},
    {"label": "E_net_plus0.3", "net": +0.3, "regime": "GROWTH"},
    {"label": "E_net_plus0.4", "net": +0.4, "regime": "GROWTH"},
    {"label": "E_net_plus0.5", "net": +0.5, "regime": "GROWTH"}
]

FREQUENCIES = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]
SEEDS = list(range(100, 110))

# Theoretical predictions
ALPHA = 607  # Hierarchical efficiency (C186)
BETA_THEORY = 2.19  # Energy power law exponent (Cycle 1472)
BETA_TOLERANCE = 0.3  # ±15% tolerance for hypothesis test

# ============================================================================
# DATA LOADING
# ============================================================================

def load_experiment_data(energy_label: str, freq: float, seed: int) -> Dict:
    """
    Load final population from single experiment database.

    Args:
        energy_label: Energy condition label (e.g., "E_net_plus0.5")
        freq: Spawn frequency
        seed: Random seed

    Returns:
        Dict with experiment metadata and final population
    """
    freq_pct = f"{freq * 100:.2f}".replace('.', '_')
    db_path = RESULTS_DIR / f"c274_2D_SWEEP_{energy_label}_f{freq_pct}pct_seed{seed}.db"

    if not db_path.exists():
        return {"error": "Database not found", "final_population": 0}

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get final cycle population
        cursor.execute("SELECT population FROM cycle_metrics ORDER BY cycle DESC LIMIT 1")
        result = cursor.fetchone()

        if result:
            final_pop = result[0]
        else:
            final_pop = 0

        conn.close()

        return {
            "energy_label": energy_label,
            "frequency": freq,
            "seed": seed,
            "final_population": final_pop
        }

    except Exception as e:
        return {"error": str(e), "final_population": 0}


def load_all_data() -> Dict:
    """
    Load all experimental results and organize by (E_net, frequency).

    Returns:
        Nested dict: {E_net: {frequency: [populations across seeds]}}
    """
    print("Loading experimental data...")

    data = {}

    for energy_cond in ENERGY_CONDITIONS:
        energy_label = energy_cond["label"]
        E_net = energy_cond["net"]

        data[E_net] = {}

        for freq in FREQUENCIES:
            populations = []

            for seed in SEEDS:
                result = load_experiment_data(energy_label, freq, seed)
                if "error" not in result:
                    populations.append(result["final_population"])

            data[E_net][freq] = populations

    print(f"✓ Loaded data for {len(ENERGY_CONDITIONS)} energy conditions, "
          f"{len(FREQUENCIES)} frequencies")

    return data


# ============================================================================
# REGIME ANALYSIS
# ============================================================================

def analyze_regimes(data: Dict) -> Dict:
    """
    Classify regimes and calculate collapse rates.

    Args:
        data: Nested dict from load_all_data()

    Returns:
        Dict with regime classifications and collapse statistics
    """
    print("\nAnalyzing regime boundaries...")

    regime_analysis = {}

    for E_net in sorted(data.keys()):
        all_pops = []
        for freq, populations in data[E_net].items():
            all_pops.extend(populations)

        n_total = len(all_pops)
        n_collapse = sum(p == 0 for p in all_pops)
        collapse_rate = n_collapse / n_total if n_total > 0 else 0

        # Classify regime
        if E_net < 0:
            expected_regime = "COLLAPSE"
        elif E_net == 0:
            expected_regime = "HOMEOSTASIS"
        else:
            expected_regime = "GROWTH"

        regime_analysis[E_net] = {
            "n_total": n_total,
            "n_collapse": n_collapse,
            "collapse_rate": collapse_rate,
            "expected_regime": expected_regime,
            "predicted_collapse": E_net < 0
        }

        print(f"E_net = {E_net:+.1f}: {n_collapse}/{n_total} collapsed "
              f"({collapse_rate*100:.1f}%), Expected: {expected_regime}")

    return regime_analysis


# ============================================================================
# POWER LAW FITTING
# ============================================================================

def fit_power_law(frequencies: np.ndarray, populations: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Fit power law: N(f) = E_∞ + A × f^-β using log transformation.

    For high-frequency regime where N approaches baseline:
    N(f) ≈ E_∞ + A/f^β

    Log transform: log(N - E_∞) = log(A) - β×log(f)

    Args:
        frequencies: Array of spawn frequencies
        populations: Array of mean populations

    Returns:
        Tuple of (β, A, E_∞, R²)
    """
    # Estimate baseline as mean of highest frequency points
    E_inf_estimate = np.mean(populations[-2:])

    # Subtract baseline
    N_shifted = populations - E_inf_estimate

    # Filter out non-positive values
    valid_mask = N_shifted > 0
    if valid_mask.sum() < 3:
        return np.nan, np.nan, E_inf_estimate, 0.0

    log_f = np.log10(frequencies[valid_mask])
    log_N = np.log10(N_shifted[valid_mask])

    # Linear regression on log-log plot
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(log_f, log_N)

    beta = -slope  # Negative because N ∝ f^-β
    A = 10 ** intercept
    r_squared = r_value ** 2

    return beta, A, E_inf_estimate, r_squared


def fit_all_conditions(data: Dict) -> Dict:
    """
    Fit power law for each E_net ≥ 0 condition.

    Args:
        data: Nested dict from load_all_data()

    Returns:
        Dict with fitted parameters for each viable E_net
    """
    print("\nFitting power laws for viable regimes (E_net ≥ 0)...")

    fits = {}

    for E_net in sorted(data.keys()):
        if E_net < 0:
            continue  # Skip collapse regimes

        # Calculate mean populations across seeds
        frequencies = np.array(sorted(data[E_net].keys()))
        mean_pops = np.array([np.mean(data[E_net][f]) for f in frequencies])

        # Fit power law
        beta, A, E_inf, r_squared = fit_power_law(frequencies, mean_pops)

        fits[E_net] = {
            "beta": beta,
            "A": A,
            "E_inf": E_inf,
            "R2": r_squared,
            "frequencies": frequencies.tolist(),
            "mean_populations": mean_pops.tolist()
        }

        # Hypothesis test: β within tolerance of theory?
        beta_min = BETA_THEORY - BETA_TOLERANCE
        beta_max = BETA_THEORY + BETA_TOLERANCE
        hypothesis_supported = beta_min <= beta <= beta_max

        print(f"E_net = {E_net:+.1f}: β = {beta:.2f}, "
              f"R² = {r_squared:.4f}, "
              f"E_∞ = {E_inf:.1f}, "
              f"A = {A:.2e} "
              f"{'✓ SUPPORTED' if hypothesis_supported else '✗ NOT SUPPORTED'}")

    return fits


# ============================================================================
# UNIVERSALITY TEST
# ============================================================================

def test_beta_universality(fits: Dict) -> Dict:
    """
    Test if β is universal (same across all E_net ≥ 0 conditions).

    Args:
        fits: Dict from fit_all_conditions()

    Returns:
        Dict with universality test results
    """
    print("\nTesting β universality...")

    beta_values = [fits[E_net]["beta"] for E_net in sorted(fits.keys())]
    E_net_values = sorted(fits.keys())

    mean_beta = np.mean(beta_values)
    std_beta = np.std(beta_values, ddof=1)
    cv_beta = std_beta / mean_beta if mean_beta > 0 else 0

    # Hypothesis test: Is mean β within tolerance?
    beta_min = BETA_THEORY - BETA_TOLERANCE
    beta_max = BETA_THEORY + BETA_TOLERANCE
    hypothesis_supported = beta_min <= mean_beta <= beta_max

    universality_result = {
        "beta_values": beta_values,
        "E_net_values": E_net_values,
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

    return universality_result


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_2d_surface(data: Dict, regime_analysis: Dict):
    """
    Plot 2D surface: (E_net, frequency) → mean population.

    Shows phase boundary at E_net = 0.
    """
    print("\nGenerating 2D surface plot...")

    # Prepare grid
    E_net_values = sorted(data.keys())
    freq_values = sorted(FREQUENCIES)

    # Calculate mean populations
    Z = np.zeros((len(E_net_values), len(freq_values)))
    for i, E_net in enumerate(E_net_values):
        for j, freq in enumerate(freq_values):
            if freq in data[E_net]:
                Z[i, j] = np.mean(data[E_net][freq])

    # Create meshgrid
    E_net_grid, freq_grid = np.meshgrid(E_net_values, freq_values, indexing='ij')

    # Plot
    fig = plt.figure(figsize=(12, 5))

    # Panel A: 2D heatmap
    ax1 = fig.add_subplot(121)
    im = ax1.contourf(freq_grid * 100, E_net_grid, Z, levels=20, cmap='viridis')
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=2, label='E_net = 0 (Phase boundary)')
    ax1.set_xlabel('Spawn Frequency (%)', fontsize=11)
    ax1.set_ylabel('Net Energy (E_net)', fontsize=11)
    ax1.set_title('A. Mean Population Across Energy-Frequency Space', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    cbar = plt.colorbar(im, ax=ax1)
    cbar.set_label('Mean Population', fontsize=10)
    ax1.set_xscale('log')

    # Panel B: Slices at different E_net values
    ax2 = fig.add_subplot(122)
    for i, E_net in enumerate(E_net_values):
        if E_net >= 0:  # Only plot viable regimes
            mean_pops = [np.mean(data[E_net][f]) for f in freq_values]
            ax2.plot(np.array(freq_values) * 100, mean_pops,
                     marker='o', label=f'E_net = {E_net:+.1f}',
                     linewidth=2, markersize=6)

    ax2.set_xlabel('Spawn Frequency (%)', fontsize=11)
    ax2.set_ylabel('Mean Population', fontsize=11)
    ax2.set_title('B. Population vs. Frequency (Viable Regimes)', fontsize=12, fontweight='bold')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c274_2d_energy_frequency_surface.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: c274_2d_energy_frequency_surface.png")
    plt.close()


def plot_power_law_fits(fits: Dict):
    """
    Plot power law fits for each E_net ≥ 0 condition.
    """
    print("Generating power law fit plots...")

    n_conditions = len(fits)
    n_cols = 3
    n_rows = (n_conditions + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 4))
    axes = axes.flatten() if n_conditions > 1 else [axes]

    for idx, (E_net, fit_data) in enumerate(sorted(fits.items())):
        ax = axes[idx]

        frequencies = np.array(fit_data["frequencies"])
        mean_pops = np.array(fit_data["mean_populations"])
        beta = fit_data["beta"]
        A = fit_data["A"]
        E_inf = fit_data["E_inf"]
        r_squared = fit_data["R2"]

        # Plot data
        ax.plot(frequencies * 100, mean_pops, 'o', markersize=8,
                label='Experimental data', color='blue')

        # Plot fit
        f_fit = np.logspace(np.log10(frequencies.min()), np.log10(frequencies.max()), 100)
        N_fit = E_inf + A / (f_fit ** beta)
        ax.plot(f_fit * 100, N_fit, '-', linewidth=2, color='red',
                label=f'Fit: N = {E_inf:.1f} + {A:.2e}/f^{beta:.2f}')

        ax.set_xlabel('Spawn Frequency (%)', fontsize=10)
        ax.set_ylabel('Mean Population', fontsize=10)
        ax.set_title(f'E_net = {E_net:+.1f} (R² = {r_squared:.4f})',
                     fontsize=11, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    # Hide unused subplots
    for idx in range(n_conditions, len(axes)):
        axes[idx].axis('off')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c274_power_law_fits_by_energy.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: c274_power_law_fits_by_energy.png")
    plt.close()


def plot_beta_universality(universality_result: Dict):
    """
    Plot β values vs. E_net to test universality.
    """
    print("Generating β universality plot...")

    beta_values = universality_result["beta_values"]
    E_net_values = universality_result["E_net_values"]
    mean_beta = universality_result["mean_beta"]
    beta_theory = universality_result["beta_theory"]

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot β values
    ax.plot(E_net_values, beta_values, 'o', markersize=10, label='Fitted β', color='blue')

    # Plot mean
    ax.axhline(y=mean_beta, color='green', linestyle='--', linewidth=2,
               label=f'Mean β = {mean_beta:.2f}')

    # Plot theory
    ax.axhline(y=beta_theory, color='red', linestyle='-', linewidth=2,
               label=f'Theory β = {beta_theory:.2f}')

    # Plot tolerance band
    ax.axhspan(beta_theory - BETA_TOLERANCE, beta_theory + BETA_TOLERANCE,
               alpha=0.2, color='red', label='±15% tolerance')

    ax.set_xlabel('Net Energy (E_net)', fontsize=12)
    ax.set_ylabel('Fitted Exponent β', fontsize=12)
    ax.set_title('β Universality Test: Energy Power Law Exponent vs. E_net',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c274_beta_universality_test.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: c274_beta_universality_test.png")
    plt.close()


def plot_baseline_amplitude_scaling(fits: Dict):
    """
    Plot E_∞(E_net) and A(E_net) to show how baseline and amplitude scale with net energy.
    """
    print("Generating baseline and amplitude scaling plots...")

    E_net_values = sorted(fits.keys())
    E_inf_values = [fits[E]["E_inf"] for E in E_net_values]
    A_values = [fits[E]["A"] for E in E_net_values]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Panel A: Baseline E_∞ vs. E_net
    ax1.plot(E_net_values, E_inf_values, 'o-', markersize=8, linewidth=2, color='blue')
    ax1.set_xlabel('Net Energy (E_net)', fontsize=11)
    ax1.set_ylabel('Baseline Population E_∞', fontsize=11)
    ax1.set_title('A. Baseline Scaling with Net Energy', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Panel B: Amplitude A vs. E_net
    ax2.plot(E_net_values, A_values, 'o-', markersize=8, linewidth=2, color='red')
    ax2.set_xlabel('Net Energy (E_net)', fontsize=11)
    ax2.set_ylabel('Amplitude A', fontsize=11)
    ax2.set_title('B. Amplitude Scaling with Net Energy', fontsize=12, fontweight='bold')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c274_baseline_amplitude_scaling.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: c274_baseline_amplitude_scaling.png")
    plt.close()


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_2d_sweep():
    """
    Complete analysis pipeline for C274 energy-frequency 2D sweep.
    """
    print("="*80)
    print("C274 ANALYSIS: 2D ENERGY-FREQUENCY SURFACE VALIDATION")
    print("="*80)

    # Load data
    data = load_all_data()

    # Analyze regimes
    regime_analysis = analyze_regimes(data)

    # Fit power laws
    fits = fit_all_conditions(data)

    # Test β universality
    universality_result = test_beta_universality(fits)

    # Visualizations
    plot_2d_surface(data, regime_analysis)
    plot_power_law_fits(fits)
    plot_beta_universality(universality_result)
    plot_baseline_amplitude_scaling(fits)

    # Save summary
    summary = {
        "regime_analysis": regime_analysis,
        "power_law_fits": {str(k): v for k, v in fits.items()},
        "universality_test": universality_result
    }

    summary_file = RESULTS_DIR / "c274_2d_sweep_analysis_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"Summary saved: {summary_file}")
    print(f"Figures saved: {FIGURES_DIR}")


if __name__ == "__main__":
    analyze_2d_sweep()
