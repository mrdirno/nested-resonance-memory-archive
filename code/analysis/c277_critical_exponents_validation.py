#!/usr/bin/env python3
"""
C277 Analysis: Critical Exponents Validation Near f_crit
==========================================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1477)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Purpose:
--------
Measure critical exponents from divergence behavior as f → f_crit:

1. Energy divergence: E_min ~ (f - f_crit)^-ν_E
2. Variance divergence: σ² ~ (f - f_crit)^-ν_σ
3. Relaxation time divergence: τ ~ (f - f_crit)^-ν_τ

Connects NRM hierarchical systems to statistical physics universality classes.

Analysis Steps:
---------------
1. Load experimental results (150 experiments, 5 frequencies)
2. Calculate mean populations, variances, relaxation times at each frequency
3. Fit power laws: X ~ (f - f_crit)^-ν
4. Extract critical exponents ν_E, ν_σ, ν_τ
5. Compare to theoretical predictions (β ≈ 2.19, γ ≈ 3.2, ν_τ ≈ 1-2)
6. Test hypothesis: Critical phenomena present?

Theoretical Predictions:
------------------------
- ν_E ≈ β ≈ 2.19 (energy critical exponent)
- ν_σ ≈ γ ≈ 3.2 (variance critical exponent)
- ν_τ ≈ 1-2 (relaxation time critical exponent, estimated)

Outputs:
--------
1. Summary JSON with fitted critical exponents
2. Figure 1: Critical divergences (3-panel: E_min, σ², τ)
3. Figure 2: Critical scaling collapse (test universality)
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

# Experimental parameters (must match C277)
F_CRIT_HIER = 0.000066  # 0.0066%
FREQUENCIES = [0.0001, 0.00015, 0.0002, 0.0003, 0.0005]
SEEDS = list(range(400, 430))

# Theoretical predictions
NU_E_THEORY = 2.19  # β
NU_SIGMA_THEORY = 3.2  # γ
NU_TAU_THEORY = 1.5  # Estimated (not derived yet)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_experiment_data(freq: float, seed: int) -> Dict:
    """Load final population and equilibration time from experiment database."""
    freq_pct = f"{freq * 100:.3f}".replace('.', '_')
    db_path = RESULTS_DIR / f"c277_CRITICAL_{freq_pct}pct_seed{seed}.db"

    if not db_path.exists():
        return {"error": "Database not found", "final_population": 0, "equilibration_time": -1}

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get final cycle population
        cursor.execute("SELECT population FROM cycle_metrics ORDER BY cycle DESC LIMIT 1")
        result = cursor.fetchone()
        final_pop = result[0] if result else 0

        # Equilibration time stored in result JSON (not in database)
        # Will be loaded from JSON file instead

        conn.close()

        return {
            "frequency": freq,
            "seed": seed,
            "final_population": final_pop
        }

    except Exception as e:
        return {"error": str(e), "final_population": 0}


def load_all_data() -> Dict:
    """Load all experimental results including equilibration times."""
    print("Loading experimental data...")

    # Load from JSON results file (contains equilibration times)
    results_file = RESULTS_DIR / "c277_critical_phenomena_results.json"

    if not results_file.exists():
        print("ERROR: Results file not found. Run C277 experiment first.")
        return {}

    with open(results_file, 'r') as f:
        results_json = json.load(f)

    # Organize by frequency
    data = {}
    for freq in FREQUENCIES:
        data[freq] = {
            "populations": [],
            "equilibration_times": []
        }

    for result in results_json["results"]:
        if "error" in result:
            continue

        freq = result["frequency"]
        if freq in data:
            data[freq]["populations"].append(result["final_population"])
            if result["equilibration_time"] > 0:
                data[freq]["equilibration_times"].append(result["equilibration_time"])

    print(f"✓ Loaded data for {len(FREQUENCIES)} frequencies")

    return data


# ============================================================================
# CRITICAL EXPONENT FITTING
# ============================================================================

def fit_power_law_divergence(
    distances: np.ndarray,
    observables: np.ndarray
) -> Tuple[float, float, float]:
    """
    Fit power law divergence: X ~ (f - f_crit)^-ν

    Args:
        distances: Array of (f - f_crit) values
        observables: Array of observable values (E_min, σ², τ)

    Returns:
        Tuple of (ν, A, R²)
    """
    # Log transform
    log_dist = np.log10(distances)
    log_obs = np.log10(observables)

    # Linear regression: log(X) = log(A) - ν × log(f - f_crit)
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(log_dist, log_obs)

    nu = -slope  # Negative because X ~ (f - f_crit)^-ν
    A = 10 ** intercept
    r_squared = r_value ** 2

    return nu, A, r_squared


def analyze_critical_phenomena(data: Dict) -> Dict:
    """Analyze critical divergences for all observables."""
    print("\nAnalyzing critical phenomena...")

    # Calculate distances from f_crit
    frequencies = np.array(sorted(data.keys()))
    distances = frequencies - F_CRIT_HIER

    # Calculate observables
    mean_pops = []
    variances = []
    mean_taus = []

    for freq in frequencies:
        pops = np.array(data[freq]["populations"])
        mean_pops.append(np.mean(pops))
        variances.append(np.var(pops, ddof=1))

        taus = data[freq]["equilibration_times"]
        if taus:
            mean_taus.append(np.mean(taus))
        else:
            mean_taus.append(np.nan)

    mean_pops = np.array(mean_pops)
    variances = np.array(variances)
    mean_taus = np.array(mean_taus)

    # Estimate E_min (inverse of population)
    E_min_proxy = 1.0 / mean_pops

    # Fit power laws
    nu_E, A_E, r2_E = fit_power_law_divergence(distances, E_min_proxy)
    nu_sigma, A_sigma, r2_sigma = fit_power_law_divergence(distances, variances)

    # Fit tau (exclude NaN values)
    tau_valid = ~np.isnan(mean_taus)
    if tau_valid.sum() >= 3:
        nu_tau, A_tau, r2_tau = fit_power_law_divergence(
            distances[tau_valid], mean_taus[tau_valid]
        )
    else:
        nu_tau, A_tau, r2_tau = np.nan, np.nan, np.nan

    # Compare to theory
    results = {
        "f_crit": F_CRIT_HIER,
        "frequencies": frequencies.tolist(),
        "distances": distances.tolist(),
        "energy": {
            "nu_fitted": nu_E,
            "nu_theory": NU_E_THEORY,
            "A": A_E,
            "R2": r2_E,
            "mean_pops": mean_pops.tolist(),
            "E_min_proxy": E_min_proxy.tolist()
        },
        "variance": {
            "nu_fitted": nu_sigma,
            "nu_theory": NU_SIGMA_THEORY,
            "A": A_sigma,
            "R2": r2_sigma,
            "variances": variances.tolist()
        },
        "relaxation": {
            "nu_fitted": nu_tau,
            "nu_theory": NU_TAU_THEORY,
            "A": A_tau,
            "R2": r2_tau,
            "mean_taus": [t if not np.isnan(t) else None for t in mean_taus]
        }
    }

    # Print summary
    print(f"\nCritical Exponents:")
    print(f"  Energy (ν_E): {nu_E:.2f} (theory: {NU_E_THEORY:.2f}), R² = {r2_E:.4f}")
    print(f"  Variance (ν_σ): {nu_sigma:.2f} (theory: {NU_SIGMA_THEORY:.2f}), R² = {r2_sigma:.4f}")
    if not np.isnan(nu_tau):
        print(f"  Relaxation (ν_τ): {nu_tau:.2f} (theory: {NU_TAU_THEORY:.2f}), R² = {r2_tau:.4f}")
    else:
        print(f"  Relaxation (ν_τ): Insufficient data")

    return results


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_critical_divergences(results: Dict):
    """Plot critical divergences for E_min, σ², and τ."""
    print("\nGenerating critical divergence plots...")

    frequencies = np.array(results["frequencies"])
    distances = np.array(results["distances"])

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Panel A: Energy divergence
    ax = axes[0]
    E_min_proxy = np.array(results["energy"]["E_min_proxy"])
    nu_E = results["energy"]["nu_fitted"]
    A_E = results["energy"]["A"]
    r2_E = results["energy"]["R2"]

    ax.loglog(distances * 100, E_min_proxy, 'o', markersize=8, label='Data', color='blue')

    # Fit line
    dist_fit = np.logspace(np.log10(distances.min()), np.log10(distances.max()), 100)
    E_fit = A_E / (dist_fit ** nu_E)
    ax.loglog(dist_fit * 100, E_fit, '-', linewidth=2, color='red',
              label=f'ν_E = {nu_E:.2f} (R² = {r2_E:.3f})')

    ax.set_xlabel('Distance from f_crit (%)', fontsize=11)
    ax.set_ylabel('E_min (proxy: 1/N)', fontsize=11)
    ax.set_title('A. Energy Divergence Near f_crit', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Panel B: Variance divergence
    ax = axes[1]
    variances = np.array(results["variance"]["variances"])
    nu_sigma = results["variance"]["nu_fitted"]
    A_sigma = results["variance"]["A"]
    r2_sigma = results["variance"]["R2"]

    ax.loglog(distances * 100, variances, 'o', markersize=8, label='Data', color='green')

    # Fit line
    sigma_fit = A_sigma / (dist_fit ** nu_sigma)
    ax.loglog(dist_fit * 100, sigma_fit, '-', linewidth=2, color='red',
              label=f'ν_σ = {nu_sigma:.2f} (R² = {r2_sigma:.3f})')

    ax.set_xlabel('Distance from f_crit (%)', fontsize=11)
    ax.set_ylabel('Variance σ²', fontsize=11)
    ax.set_title('B. Variance Divergence Near f_crit', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Panel C: Relaxation time divergence
    ax = axes[2]
    mean_taus = results["relaxation"]["mean_taus"]
    nu_tau = results["relaxation"]["nu_fitted"]
    A_tau = results["relaxation"]["A"]
    r2_tau = results["relaxation"]["R2"]

    # Filter valid tau values
    tau_array = np.array([t if t is not None else np.nan for t in mean_taus])
    valid_mask = ~np.isnan(tau_array)

    if valid_mask.sum() >= 3:
        ax.loglog(distances[valid_mask] * 100, tau_array[valid_mask], 'o',
                  markersize=8, label='Data', color='purple')

        # Fit line
        tau_fit = A_tau / (dist_fit ** nu_tau)
        ax.loglog(dist_fit * 100, tau_fit, '-', linewidth=2, color='red',
                  label=f'ν_τ = {nu_tau:.2f} (R² = {r2_tau:.3f})')

        ax.set_xlabel('Distance from f_crit (%)', fontsize=11)
        ax.set_ylabel('Relaxation Time τ (cycles)', fontsize=11)
        ax.set_title('C. Critical Slowing Down Near f_crit', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'Insufficient equilibration data',
                ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.set_title('C. Critical Slowing Down Near f_crit', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "c277_critical_divergences.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: c277_critical_divergences.png")
    plt.close()


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_critical_exponents():
    """Complete critical exponents analysis for C277."""
    print("="*80)
    print("C277 ANALYSIS: CRITICAL EXPONENTS VALIDATION")
    print("="*80)

    # Load data
    data = load_all_data()

    if not data:
        print("ERROR: No data available. Exiting.")
        return

    # Analyze critical phenomena
    results = analyze_critical_phenomena(data)

    # Visualization
    plot_critical_divergences(results)

    # Save summary
    summary_file = RESULTS_DIR / "c277_critical_exponents_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"Summary saved: {summary_file}")
    print(f"Figures saved: {FIGURES_DIR}")


if __name__ == "__main__":
    analyze_critical_exponents()
