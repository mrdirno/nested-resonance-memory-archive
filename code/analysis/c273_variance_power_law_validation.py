#!/usr/bin/env python3
"""
C273 Variance Power Law Validation Analysis
===========================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1473)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Analyze C273 extended frequency-variance mapping results to validate
power law exponent γ ≈ 3.2 predicted by unified scaling framework.

Analysis:
---------
1. Load experimental results (200 experiments across 10 frequencies)
2. Calculate variance σ² at each frequency point
3. Fit power law: σ²(f) = A × f^-γ using log-log linear regression
4. Compare fitted γ to theoretical prediction γ = β + 1 = 3.19
5. Generate publication-quality visualization
6. Test for systematic deviations at frequency extremes

Hypothesis Test:
----------------
H0: γ = 3.19 (unified framework prediction)
H1: γ ≠ 3.19 (power law holds but with different exponent)

Success Criteria:
-----------------
- Fitted γ within 10% of prediction: 2.9 < γ < 3.5
- R² > 0.90 (strong power law fit)
- Residuals show no systematic trend with frequency
"""

import json
import sqlite3
import numpy as np
from pathlib import Path
from scipy import stats as scipy_stats
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
FIGURES_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Theoretical prediction
BETA_THEORY = 2.19  # Energy power law exponent (Cycle 1399)
GAMMA_THEORY = BETA_THEORY + 1  # Variance power law exponent (Cycle 1471 derivation)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_experiment_final_pop(freq: float, seed: int) -> int:
    """
    Load final population from experiment database.

    Args:
        freq: Spawn frequency (0.0001 - 0.10)
        seed: Random seed

    Returns:
        Final population count
    """
    # Format frequency for filename (0.01% -> 0_01pct)
    freq_pct = f"{freq * 100:.2f}".replace('.', '_')
    db_file = RESULTS_DIR / f"c273_v6b_EXTENDED_VARIANCE_{freq_pct}pct_seed{seed}.db"

    if not db_file.exists():
        return None

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get final population from results table
        cursor.execute("""
            SELECT population FROM results
            ORDER BY cycle DESC
            LIMIT 1
        """)

        result = cursor.fetchone()
        final_pop = result[0] if result else 0
        conn.close()

        return final_pop

    except Exception as e:
        print(f"Error loading {db_file}: {e}")
        return None


def load_all_results(frequencies: List[float], seeds: List[int]) -> Dict[float, List[int]]:
    """
    Load all experimental results.

    Args:
        frequencies: List of spawn frequencies
        seeds: List of random seeds

    Returns:
        Dict mapping frequency -> list of final populations
    """
    results = {f: [] for f in frequencies}

    print("Loading experimental results...")
    for freq in frequencies:
        print(f"\nFrequency {freq*100:.2f}%:")

        for seed in seeds:
            pop = load_experiment_final_pop(freq, seed)

            if pop is not None:
                results[freq].append(pop)

        n = len(results[freq])
        if n > 0:
            mean = np.mean(results[freq])
            std = np.std(results[freq], ddof=1)
            print(f"  Loaded {n}/{len(seeds)} experiments: μ={mean:.1f}, σ={std:.1f}")
        else:
            print(f"  ⚠ No experiments found for f={freq*100:.2f}%")

    return results


# ============================================================================
# POWER LAW FITTING
# ============================================================================

def fit_power_law(frequencies: np.ndarray, variances: np.ndarray) -> Tuple[float, float, float]:
    """
    Fit power law: σ²(f) = A × f^-γ using log-log linear regression.

    Args:
        frequencies: Array of spawn frequencies
        variances: Array of population variances

    Returns:
        Tuple of (γ, A, R²)
    """
    # Log-log transform
    log_f = np.log10(frequencies)
    log_var = np.log10(variances)

    # Linear regression in log-log space
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(log_f, log_var)

    # Power law parameters
    gamma = -slope  # Negative because σ² ∝ f^-γ
    A = 10 ** intercept
    r_squared = r_value ** 2

    return gamma, A, r_squared


def calculate_variance_statistics(results: Dict[float, List[int]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate variance statistics at each frequency.

    Args:
        results: Dict mapping frequency -> list of populations

    Returns:
        Tuple of (frequencies, variances, means, stds)
    """
    frequencies = []
    variances = []
    means = []
    stds = []

    for freq, pops in sorted(results.items()):
        if len(pops) >= 3:  # Need at least 3 samples for variance
            pops_array = np.array(pops)

            frequencies.append(freq)
            means.append(np.mean(pops_array))
            stds.append(np.std(pops_array, ddof=1))
            variances.append(np.var(pops_array, ddof=1))

    return (np.array(frequencies), np.array(variances),
            np.array(means), np.array(stds))


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_power_law_fit(
    frequencies: np.ndarray,
    variances: np.ndarray,
    gamma_fit: float,
    A_fit: float,
    r_squared: float
):
    """
    Generate publication-quality power law fit visualization.

    Args:
        frequencies: Array of spawn frequencies
        variances: Array of population variances
        gamma_fit: Fitted exponent
        A_fit: Fitted amplitude
        r_squared: R² goodness of fit
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    # Panel A: Log-log plot with power law fit
    ax1 = axes[0]

    # Data points
    ax1.loglog(frequencies * 100, variances, 'o', markersize=8,
               color='steelblue', label='Empirical variance')

    # Fitted power law
    f_fit = np.logspace(np.log10(frequencies.min()), np.log10(frequencies.max()), 100)
    var_fit = A_fit * (f_fit ** (-gamma_fit))

    ax1.loglog(f_fit * 100, var_fit, '-', linewidth=2, color='crimson',
               label=f'Power law fit: σ² ∝ f$^{{-{gamma_fit:.2f}}}$')

    # Theoretical prediction line
    var_theory = A_fit * (f_fit ** (-GAMMA_THEORY))
    ax1.loglog(f_fit * 100, var_theory, '--', linewidth=2, color='gray', alpha=0.7,
               label=f'Theory: γ = {GAMMA_THEORY:.2f}')

    ax1.set_xlabel('Spawn Frequency (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Population Variance (σ²)', fontsize=12, fontweight='bold')
    ax1.set_title(f'Power Law Scaling (R² = {r_squared:.4f})',
                  fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='best')
    ax1.grid(True, alpha=0.3, which='both')

    # Panel B: Residuals plot
    ax2 = axes[1]

    # Calculate residuals
    var_predicted = A_fit * (frequencies ** (-gamma_fit))
    residuals = (variances - var_predicted) / var_predicted * 100  # Percentage residuals

    ax2.semilogx(frequencies * 100, residuals, 'o', markersize=8, color='steelblue')
    ax2.axhline(y=0, color='gray', linestyle='--', linewidth=2)

    ax2.set_xlabel('Spawn Frequency (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Residuals (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Fit Quality (Residual Analysis)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, which='both')

    plt.tight_layout()

    # Save figure
    output_file = FIGURES_DIR / "c273_variance_power_law_validation.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Figure saved: {output_file}")

    plt.close()


def plot_variance_vs_frequency_panels(
    frequencies: np.ndarray,
    variances: np.ndarray,
    means: np.ndarray,
    stds: np.ndarray,
    gamma_fit: float,
    A_fit: float
):
    """
    Generate multi-panel visualization showing variance scaling across frequencies.

    Args:
        frequencies: Array of spawn frequencies
        variances: Array of population variances
        means: Array of population means
        stds: Array of population standard deviations
        gamma_fit: Fitted exponent
        A_fit: Fitted amplitude
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=300)

    # Panel A: Variance vs Frequency (log-log)
    ax1 = axes[0, 0]
    ax1.loglog(frequencies * 100, variances, 'o-', markersize=8,
               linewidth=2, color='steelblue')
    ax1.set_xlabel('Spawn Frequency (%)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Population Variance (σ²)', fontsize=11, fontweight='bold')
    ax1.set_title('A: Variance Scaling', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, which='both')

    # Panel B: Standard Deviation vs Frequency (log-log)
    ax2 = axes[0, 1]
    ax2.loglog(frequencies * 100, stds, 'o-', markersize=8,
               linewidth=2, color='forestgreen')
    ax2.set_xlabel('Spawn Frequency (%)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Standard Deviation (σ)', fontsize=11, fontweight='bold')
    ax2.set_title('B: Std Dev Scaling (σ ∝ f$^{-γ/2}$)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, which='both')

    # Panel C: Coefficient of Variation (CV) vs Frequency
    ax3 = axes[1, 0]
    cv = stds / means
    ax3.semilogx(frequencies * 100, cv, 'o-', markersize=8,
                 linewidth=2, color='darkred')
    ax3.set_xlabel('Spawn Frequency (%)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Coefficient of Variation (CV = σ/μ)', fontsize=11, fontweight='bold')
    ax3.set_title('C: Normalized Variance', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # Panel D: Mean Population vs Frequency
    ax4 = axes[1, 1]
    ax4.semilogx(frequencies * 100, means, 'o-', markersize=8,
                 linewidth=2, color='purple')
    ax4.set_xlabel('Spawn Frequency (%)', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Mean Population', fontsize=11, fontweight='bold')
    ax4.set_title('D: Population Response', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save figure
    output_file = FIGURES_DIR / "c273_variance_scaling_panels.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Figure saved: {output_file}")

    plt.close()


# ============================================================================
# ANALYSIS
# ============================================================================

def analyze_variance_power_law(
    frequencies: List[float],
    seeds: List[int]
):
    """
    Complete variance power law validation analysis.

    Args:
        frequencies: List of spawn frequencies tested
        seeds: List of random seeds used
    """
    print("="*80)
    print("C273 VARIANCE POWER LAW VALIDATION")
    print("="*80)

    # Load experimental results
    results = load_all_results(frequencies, seeds)

    # Calculate variance statistics
    freqs, variances, means, stds = calculate_variance_statistics(results)

    if len(freqs) < 3:
        print("\n⚠ ERROR: Need at least 3 frequency points for power law fitting")
        return

    print(f"\n{'='*80}")
    print("VARIANCE STATISTICS")
    print(f"{'='*80}")

    print(f"\n{'Frequency (%)':<15} {'Mean Pop':<12} {'Std Dev':<12} {'Variance':<12} {'CV':<10}")
    print("-" * 65)
    for i, freq in enumerate(freqs):
        cv = stds[i] / means[i] if means[i] > 0 else 0
        print(f"{freq*100:>14.2f} {means[i]:>11.1f} {stds[i]:>11.1f} {variances[i]:>11.1f} {cv:>9.4f}")

    # Fit power law
    gamma_fit, A_fit, r_squared = fit_power_law(freqs, variances)

    print(f"\n{'='*80}")
    print("POWER LAW FIT RESULTS")
    print(f"{'='*80}")

    print(f"\nFitted Model: σ²(f) = A × f^(-γ)")
    print(f"  Amplitude (A): {A_fit:.2e}")
    print(f"  Exponent (γ): {gamma_fit:.3f}")
    print(f"  R²: {r_squared:.6f}")

    print(f"\nTheoretical Prediction:")
    print(f"  β (energy exponent): {BETA_THEORY}")
    print(f"  γ = β + 1: {GAMMA_THEORY:.3f}")

    print(f"\nComparison:")
    print(f"  Fitted γ: {gamma_fit:.3f}")
    print(f"  Theory γ: {GAMMA_THEORY:.3f}")
    print(f"  Difference: {abs(gamma_fit - GAMMA_THEORY):.3f} ({abs(gamma_fit - GAMMA_THEORY)/GAMMA_THEORY*100:.1f}%)")

    # Hypothesis test
    tolerance = 0.10  # 10% tolerance
    gamma_min = GAMMA_THEORY * (1 - tolerance)
    gamma_max = GAMMA_THEORY * (1 + tolerance)

    print(f"\n{'='*80}")
    print("HYPOTHESIS TEST")
    print(f"{'='*80}")

    print(f"\nH0: γ = {GAMMA_THEORY:.2f} ± {tolerance*100:.0f}% (unified framework prediction)")
    print(f"Acceptance region: {gamma_min:.2f} < γ < {gamma_max:.2f}")
    print(f"Fitted γ: {gamma_fit:.3f}")

    if gamma_min <= gamma_fit <= gamma_max:
        print(f"\n✓ HYPOTHESIS SUPPORTED: γ within {tolerance*100:.0f}% of prediction")
        print(f"  Unified framework prediction validated!")
    else:
        print(f"\n✗ HYPOTHESIS NOT SUPPORTED: γ outside {tolerance*100:.0f}% tolerance")
        print(f"  May indicate frequency-dependent corrections or regime effects")

    if r_squared > 0.90:
        print(f"✓ STRONG POWER LAW FIT: R² = {r_squared:.4f} > 0.90")
    else:
        print(f"⚠ WEAK POWER LAW FIT: R² = {r_squared:.4f} < 0.90")
        print(f"  May indicate non-power-law behavior or systematic deviations")

    # Generate visualizations
    print(f"\n{'='*80}")
    print("GENERATING FIGURES")
    print(f"{'='*80}")

    plot_power_law_fit(freqs, variances, gamma_fit, A_fit, r_squared)
    plot_variance_vs_frequency_panels(freqs, variances, means, stds, gamma_fit, A_fit)

    # Save summary
    summary = {
        "fitted_gamma": gamma_fit,
        "fitted_A": A_fit,
        "r_squared": r_squared,
        "theory_gamma": GAMMA_THEORY,
        "gamma_difference": abs(gamma_fit - GAMMA_THEORY),
        "gamma_percent_error": abs(gamma_fit - GAMMA_THEORY) / GAMMA_THEORY * 100,
        "hypothesis_supported": gamma_min <= gamma_fit <= gamma_max,
        "fit_quality": "strong" if r_squared > 0.90 else "weak",
        "n_frequencies": len(freqs),
        "frequency_range": [float(freqs.min()), float(freqs.max())],
        "variance_range": [float(variances.min()), float(variances.max())]
    }

    summary_file = RESULTS_DIR / "c273_variance_power_law_analysis_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Analysis summary saved: {summary_file}")

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Frequencies tested in C273
    FREQUENCIES = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10]
    SEEDS = list(range(42, 62))

    analyze_variance_power_law(FREQUENCIES, SEEDS)
