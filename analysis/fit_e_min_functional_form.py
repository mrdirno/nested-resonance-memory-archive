#!/usr/bin/env python3
"""
Functional Form Fitting: E_min vs f_spawn Relationship

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0

CYCLE 1399: FIT FUNCTIONAL FORMS TO E_MIN(F_SPAWN) DATA

Purpose:
--------
Characterize the functional relationship between minimum viable energy
per agent (E_min) and spawn frequency (f_spawn) discovered in Cycle 1398.

Two candidate models:
1. Inverse power law: E_min(f) = E_∞ + A / f^α
2. Exponential decay: E_min(f) = E_∞ + B × exp(-β × f)

Methods:
--------
- Non-linear least squares fitting (scipy.optimize.curve_fit)
- Model comparison: AIC, R², RMSE
- Residual analysis
- Prediction generation with confidence intervals
- Publication-quality visualization (300 DPI)

Data Source:
------------
140 experiments from Cycle 1398 analysis:
- V6b: 50 experiments (spawn_cost=5.0, varying f_spawn)
- V6c: 50 experiments (spawn_cost=7.5, varying f_spawn)
- spawn_cost: 40 experiments (f_spawn=0.005, varying spawn_cost)

Expected Pattern:
-----------------
E_min decreases with f_spawn (inverse relationship)
- f_spawn=0.001 → E_min ≈ 583 units
- f_spawn=0.01 → E_min ≈ 500.6 units
- Asymptotic minimum: E_min → ~500.5 as f_spawn → ∞
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit
from scipy import stats
from datetime import datetime

# ============================================================================
# PATHS
# ============================================================================

RESULTS_FILE = Path('/Volumes/dual/DUALITY-ZERO-V2/analysis/e_min_universality/e_min_universality_results.json')
OUTPUT_DIR = Path('/Volumes/dual/DUALITY-ZERO-V2/analysis/e_min_functional_form')
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# FUNCTIONAL FORMS
# ============================================================================

def inverse_power_law(f, E_inf, A, alpha):
    """
    Inverse power law model.

    E_min(f) = E_∞ + A / f^α

    Parameters:
    -----------
    f : array_like
        Spawn frequency values
    E_inf : float
        Asymptotic minimum energy (E_∞)
    A : float
        Amplitude coefficient
    alpha : float
        Power law exponent

    Returns:
    --------
    E_min : array_like
        Predicted minimum viable energy
    """
    return E_inf + A / (f ** alpha)


def exponential_decay(f, E_inf, B, beta):
    """
    Exponential decay model.

    E_min(f) = E_∞ + B × exp(-β × f)

    Parameters:
    -----------
    f : array_like
        Spawn frequency values
    E_inf : float
        Asymptotic minimum energy (E_∞)
    B : float
        Amplitude coefficient
    beta : float
        Decay rate

    Returns:
    --------
    E_min : array_like
        Predicted minimum viable energy
    """
    return E_inf + B * np.exp(-beta * f)


# ============================================================================
# MODEL FITTING AND COMPARISON
# ============================================================================

def fit_models(f_spawn_values, e_min_means, e_min_stds):
    """
    Fit both functional forms to E_min vs f_spawn data.

    Parameters:
    -----------
    f_spawn_values : array_like
        Spawn frequency values
    e_min_means : array_like
        Mean E_min for each f_spawn
    e_min_stds : array_like
        Standard deviation of E_min for each f_spawn

    Returns:
    --------
    results : dict
        Fit parameters, goodness-of-fit metrics, predictions
    """

    # Convert to numpy arrays
    f = np.array(f_spawn_values)
    e_min = np.array(e_min_means)
    sigma = np.array(e_min_stds)

    print("="*80)
    print("FITTING FUNCTIONAL FORMS TO E_MIN(F_SPAWN)")
    print("="*80)
    print(f"\nData points: {len(f)}")
    print(f"f_spawn range: [{f.min():.4f}, {f.max():.4f}]")
    print(f"E_min range: [{e_min.min():.2f}, {e_min.max():.2f}]")

    # ========================================================================
    # FIT 1: INVERSE POWER LAW
    # ========================================================================

    print("\n" + "-"*80)
    print("MODEL 1: INVERSE POWER LAW")
    print("E_min(f) = E_∞ + A / f^α")
    print("-"*80)

    # Initial parameter guesses
    # E_inf ≈ 500.5 (asymptotic minimum from Cycle 1398)
    # A ≈ 0.08 (rough estimate from data)
    # alpha ≈ 1.0 (simple inverse relationship)
    p0_power = [500.5, 0.08, 1.0]

    try:
        popt_power, pcov_power = curve_fit(
            inverse_power_law,
            f,
            e_min,
            p0=p0_power,
            sigma=sigma,
            absolute_sigma=True,
            maxfev=10000
        )

        E_inf_power, A_power, alpha_power = popt_power
        perr_power = np.sqrt(np.diag(pcov_power))

        print(f"\nFitted parameters:")
        print(f"  E_∞ = {E_inf_power:.4f} ± {perr_power[0]:.4f} units")
        print(f"  A   = {A_power:.6f} ± {perr_power[1]:.6f}")
        print(f"  α   = {alpha_power:.4f} ± {perr_power[2]:.4f}")

        # Predictions
        e_min_pred_power = inverse_power_law(f, *popt_power)
        residuals_power = e_min - e_min_pred_power

        # Goodness of fit
        ss_res_power = np.sum(residuals_power**2)
        ss_tot = np.sum((e_min - np.mean(e_min))**2)
        r_squared_power = 1 - (ss_res_power / ss_tot)
        rmse_power = np.sqrt(np.mean(residuals_power**2))

        # AIC: Akaike Information Criterion
        # AIC = n * ln(RSS/n) + 2k
        n = len(f)
        k_power = 3  # number of parameters
        aic_power = n * np.log(ss_res_power / n) + 2 * k_power

        print(f"\nGoodness of fit:")
        print(f"  R² = {r_squared_power:.6f}")
        print(f"  RMSE = {rmse_power:.4f} units")
        print(f"  AIC = {aic_power:.2f}")

        power_law_success = True

    except Exception as e:
        print(f"\n❌ Power law fit FAILED: {e}")
        power_law_success = False
        popt_power = None
        r_squared_power = None
        rmse_power = None
        aic_power = None

    # ========================================================================
    # FIT 2: EXPONENTIAL DECAY
    # ========================================================================

    print("\n" + "-"*80)
    print("MODEL 2: EXPONENTIAL DECAY")
    print("E_min(f) = E_∞ + B × exp(-β × f)")
    print("-"*80)

    # Initial parameter guesses
    # E_inf ≈ 500.5
    # B ≈ 82 (e_min_max - e_min_min ≈ 583 - 500.6)
    # beta ≈ 100 (decay rate estimate)
    p0_exp = [500.5, 82.0, 100.0]

    try:
        popt_exp, pcov_exp = curve_fit(
            exponential_decay,
            f,
            e_min,
            p0=p0_exp,
            sigma=sigma,
            absolute_sigma=True,
            maxfev=10000
        )

        E_inf_exp, B_exp, beta_exp = popt_exp
        perr_exp = np.sqrt(np.diag(pcov_exp))

        print(f"\nFitted parameters:")
        print(f"  E_∞ = {E_inf_exp:.4f} ± {perr_exp[0]:.4f} units")
        print(f"  B   = {B_exp:.4f} ± {perr_exp[1]:.4f}")
        print(f"  β   = {beta_exp:.2f} ± {perr_exp[2]:.2f}")

        # Predictions
        e_min_pred_exp = exponential_decay(f, *popt_exp)
        residuals_exp = e_min - e_min_pred_exp

        # Goodness of fit
        ss_res_exp = np.sum(residuals_exp**2)
        r_squared_exp = 1 - (ss_res_exp / ss_tot)
        rmse_exp = np.sqrt(np.mean(residuals_exp**2))

        # AIC
        k_exp = 3  # number of parameters
        aic_exp = n * np.log(ss_res_exp / n) + 2 * k_exp

        print(f"\nGoodness of fit:")
        print(f"  R² = {r_squared_exp:.6f}")
        print(f"  RMSE = {rmse_exp:.4f} units")
        print(f"  AIC = {aic_exp:.2f}")

        exp_decay_success = True

    except Exception as e:
        print(f"\n❌ Exponential decay fit FAILED: {e}")
        exp_decay_success = False
        popt_exp = None
        r_squared_exp = None
        rmse_exp = None
        aic_exp = None

    # ========================================================================
    # MODEL COMPARISON
    # ========================================================================

    print("\n" + "="*80)
    print("MODEL COMPARISON")
    print("="*80)

    if power_law_success and exp_decay_success:
        print("\nR² (higher is better):")
        print(f"  Power law:     R² = {r_squared_power:.6f}")
        print(f"  Exponential:   R² = {r_squared_exp:.6f}")
        if r_squared_power > r_squared_exp:
            print(f"  → Power law WINS by ΔR² = {r_squared_power - r_squared_exp:.6f}")
        else:
            print(f"  → Exponential WINS by ΔR² = {r_squared_exp - r_squared_power:.6f}")

        print("\nRMSE (lower is better):")
        print(f"  Power law:     RMSE = {rmse_power:.4f} units")
        print(f"  Exponential:   RMSE = {rmse_exp:.4f} units")
        if rmse_power < rmse_exp:
            print(f"  → Power law WINS by ΔRMSE = {rmse_exp - rmse_power:.4f} units")
        else:
            print(f"  → Exponential WINS by ΔRMSE = {rmse_power - rmse_exp:.4f} units")

        print("\nAIC (lower is better):")
        print(f"  Power law:     AIC = {aic_power:.2f}")
        print(f"  Exponential:   AIC = {aic_exp:.2f}")
        delta_aic = abs(aic_power - aic_exp)
        if aic_power < aic_exp:
            print(f"  → Power law WINS by ΔAIC = {delta_aic:.2f}")
        else:
            print(f"  → Exponential WINS by ΔAIC = {delta_aic:.2f}")

        # AIC interpretation
        print("\nAIC interpretation:")
        if delta_aic < 2:
            print("  ΔAIC < 2: Models are EQUIVALENT (indistinguishable)")
        elif delta_aic < 4:
            print("  2 < ΔAIC < 4: Weak evidence for better model")
        elif delta_aic < 7:
            print("  4 < ΔAIC < 7: Moderate evidence for better model")
        else:
            print("  ΔAIC > 7: Strong evidence for better model")

        # Overall verdict
        print("\n" + "-"*80)
        print("VERDICT:")
        wins = {'power': 0, 'exp': 0}
        if r_squared_power > r_squared_exp:
            wins['power'] += 1
        else:
            wins['exp'] += 1
        if rmse_power < rmse_exp:
            wins['power'] += 1
        else:
            wins['exp'] += 1
        if aic_power < aic_exp:
            wins['power'] += 1
        else:
            wins['exp'] += 1

        if wins['power'] > wins['exp']:
            print(f"✓ INVERSE POWER LAW is preferred model ({wins['power']}/3 metrics)")
        elif wins['exp'] > wins['power']:
            print(f"✓ EXPONENTIAL DECAY is preferred model ({wins['exp']}/3 metrics)")
        else:
            print("✓ Models are TIED (further investigation needed)")
        print("-"*80)

    # ========================================================================
    # GENERATE PREDICTIONS
    # ========================================================================

    print("\n" + "="*80)
    print("GENERATING PREDICTIONS")
    print("="*80)

    # Fine grid for smooth curves
    f_fine = np.linspace(f.min(), f.max(), 1000)

    predictions = {}

    if power_law_success:
        e_min_fine_power = inverse_power_law(f_fine, *popt_power)
        predictions['power_law'] = {
            'f_spawn': f_fine.tolist(),
            'e_min': e_min_fine_power.tolist(),
            'parameters': {
                'E_inf': float(popt_power[0]),
                'A': float(popt_power[1]),
                'alpha': float(popt_power[2])
            },
            'uncertainties': {
                'E_inf_err': float(perr_power[0]),
                'A_err': float(perr_power[1]),
                'alpha_err': float(perr_power[2])
            },
            'metrics': {
                'r_squared': float(r_squared_power),
                'rmse': float(rmse_power),
                'aic': float(aic_power)
            }
        }

        print("\nPower law predictions at intermediate f_spawn:")
        test_f = [0.003, 0.006, 0.008]
        for f_test in test_f:
            e_pred = inverse_power_law(f_test, *popt_power)
            print(f"  f_spawn = {f_test:.4f} → E_min = {e_pred:.2f} units")

    if exp_decay_success:
        e_min_fine_exp = exponential_decay(f_fine, *popt_exp)
        predictions['exponential'] = {
            'f_spawn': f_fine.tolist(),
            'e_min': e_min_fine_exp.tolist(),
            'parameters': {
                'E_inf': float(popt_exp[0]),
                'B': float(popt_exp[1]),
                'beta': float(popt_exp[2])
            },
            'uncertainties': {
                'E_inf_err': float(perr_exp[0]),
                'B_err': float(perr_exp[1]),
                'beta_err': float(perr_exp[2])
            },
            'metrics': {
                'r_squared': float(r_squared_exp),
                'rmse': float(rmse_exp),
                'aic': float(aic_exp)
            }
        }

        print("\nExponential decay predictions at intermediate f_spawn:")
        test_f = [0.003, 0.006, 0.008]
        for f_test in test_f:
            e_pred = exponential_decay(f_test, *popt_exp)
            print(f"  f_spawn = {f_test:.4f} → E_min = {e_pred:.2f} units")

    # ========================================================================
    # ASSEMBLE RESULTS
    # ========================================================================

    results = {
        'data': {
            'f_spawn': f.tolist(),
            'e_min_mean': e_min.tolist(),
            'e_min_std': sigma.tolist()
        },
        'fits': predictions,
        'comparison': {}
    }

    if power_law_success and exp_decay_success:
        results['comparison'] = {
            'r_squared': {
                'power_law': float(r_squared_power),
                'exponential': float(r_squared_exp),
                'delta': float(abs(r_squared_power - r_squared_exp))
            },
            'rmse': {
                'power_law': float(rmse_power),
                'exponential': float(rmse_exp),
                'delta': float(abs(rmse_power - rmse_exp))
            },
            'aic': {
                'power_law': float(aic_power),
                'exponential': float(aic_exp),
                'delta': float(abs(aic_power - aic_exp))
            },
            'preferred_model': 'power_law' if wins['power'] > wins['exp'] else 'exponential' if wins['exp'] > wins['power'] else 'tied'
        }

    return results


# ============================================================================
# VISUALIZATION
# ============================================================================

def create_visualization(results, output_path):
    """
    Create publication-quality 4-panel figure.

    Panels:
    1. Data + both model fits
    2. Residuals comparison
    3. Model predictions (extended range)
    4. Parameter sensitivity
    """

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('E_min vs f_spawn: Functional Form Analysis (Cycle 1399)',
                 fontsize=14, fontweight='bold')

    # Extract data
    f_data = np.array(results['data']['f_spawn'])
    e_min_data = np.array(results['data']['e_min_mean'])
    e_min_std = np.array(results['data']['e_min_std'])

    has_power = 'power_law' in results['fits']
    has_exp = 'exponential' in results['fits']

    # ========================================================================
    # PANEL 1: DATA + MODEL FITS
    # ========================================================================

    ax = axes[0, 0]

    # Data points with error bars
    ax.errorbar(f_data, e_min_data, yerr=e_min_std,
                fmt='o', color='black', markersize=8,
                capsize=5, capthick=2, label='Data (N=140 exp)',
                zorder=10)

    # Model fits
    if has_power:
        f_fine = np.array(results['fits']['power_law']['f_spawn'])
        e_fine = np.array(results['fits']['power_law']['e_min'])
        r2 = results['fits']['power_law']['metrics']['r_squared']
        ax.plot(f_fine, e_fine, '-', color='blue', linewidth=2,
                label=f'Power law (R²={r2:.4f})', alpha=0.8)

    if has_exp:
        f_fine = np.array(results['fits']['exponential']['f_spawn'])
        e_fine = np.array(results['fits']['exponential']['e_min'])
        r2 = results['fits']['exponential']['metrics']['r_squared']
        ax.plot(f_fine, e_fine, '--', color='red', linewidth=2,
                label=f'Exponential (R²={r2:.4f})', alpha=0.8)

    ax.set_xlabel('f_spawn (spawn frequency)', fontsize=11, fontweight='bold')
    ax.set_ylabel('E_min (energy/agent)', fontsize=11, fontweight='bold')
    ax.set_title('Functional Form Fits', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)

    # ========================================================================
    # PANEL 2: RESIDUALS
    # ========================================================================

    ax = axes[0, 1]

    if has_power:
        e_pred_power = inverse_power_law(f_data,
                                         results['fits']['power_law']['parameters']['E_inf'],
                                         results['fits']['power_law']['parameters']['A'],
                                         results['fits']['power_law']['parameters']['alpha'])
        residuals_power = e_min_data - e_pred_power
        ax.plot(f_data, residuals_power, 'o-', color='blue',
                label='Power law', markersize=8, linewidth=1.5)

    if has_exp:
        e_pred_exp = exponential_decay(f_data,
                                       results['fits']['exponential']['parameters']['E_inf'],
                                       results['fits']['exponential']['parameters']['B'],
                                       results['fits']['exponential']['parameters']['beta'])
        residuals_exp = e_min_data - e_pred_exp
        ax.plot(f_data, residuals_exp, 's--', color='red',
                label='Exponential', markersize=8, linewidth=1.5)

    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax.set_xlabel('f_spawn', fontsize=11, fontweight='bold')
    ax.set_ylabel('Residuals (Data - Model)', fontsize=11, fontweight='bold')
    ax.set_title('Residual Analysis', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)

    # ========================================================================
    # PANEL 3: EXTENDED PREDICTIONS
    # ========================================================================

    ax = axes[1, 0]

    # Extended f_spawn range for extrapolation visualization
    f_extended = np.linspace(0.0005, 0.02, 1000)

    # Data region shading
    ax.axvspan(f_data.min(), f_data.max(), alpha=0.1, color='gray',
               label='Data region')

    if has_power:
        params = results['fits']['power_law']['parameters']
        e_extended_power = inverse_power_law(f_extended,
                                            params['E_inf'],
                                            params['A'],
                                            params['alpha'])
        ax.plot(f_extended, e_extended_power, '-', color='blue',
                linewidth=2, label='Power law (extended)', alpha=0.8)

        # Asymptote
        ax.axhline(y=params['E_inf'], color='blue', linestyle=':',
                   linewidth=1.5, alpha=0.6,
                   label=f'Asymptote: E_∞={params["E_inf"]:.2f}')

    if has_exp:
        params = results['fits']['exponential']['parameters']
        e_extended_exp = exponential_decay(f_extended,
                                          params['E_inf'],
                                          params['B'],
                                          params['beta'])
        ax.plot(f_extended, e_extended_exp, '--', color='red',
                linewidth=2, label='Exponential (extended)', alpha=0.8)

        # Asymptote
        ax.axhline(y=params['E_inf'], color='red', linestyle=':',
                   linewidth=1.5, alpha=0.6,
                   label=f'Asymptote: E_∞={params["E_inf"]:.2f}')

    # Mark test points
    test_f = [0.003, 0.006, 0.008]
    for f_test in test_f:
        ax.axvline(x=f_test, color='orange', linestyle=':',
                   linewidth=1, alpha=0.5)

    ax.set_xlabel('f_spawn (extended range)', fontsize=11, fontweight='bold')
    ax.set_ylabel('E_min (energy/agent)', fontsize=11, fontweight='bold')
    ax.set_title('Model Predictions (Extended Range)', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 0.02)

    # ========================================================================
    # PANEL 4: MODEL COMPARISON METRICS
    # ========================================================================

    ax = axes[1, 1]
    ax.axis('off')

    # Create comparison table
    comparison_text = "MODEL COMPARISON\n" + "="*50 + "\n\n"

    if has_power and has_exp:
        comp = results['comparison']

        comparison_text += "R² (Coefficient of Determination):\n"
        comparison_text += f"  Power law:     {comp['r_squared']['power_law']:.6f}\n"
        comparison_text += f"  Exponential:   {comp['r_squared']['exponential']:.6f}\n"
        comparison_text += f"  ΔR² = {comp['r_squared']['delta']:.6f}\n\n"

        comparison_text += "RMSE (Root Mean Square Error):\n"
        comparison_text += f"  Power law:     {comp['rmse']['power_law']:.4f} units\n"
        comparison_text += f"  Exponential:   {comp['rmse']['exponential']:.4f} units\n"
        comparison_text += f"  ΔRMSE = {comp['rmse']['delta']:.4f} units\n\n"

        comparison_text += "AIC (Akaike Information Criterion):\n"
        comparison_text += f"  Power law:     {comp['aic']['power_law']:.2f}\n"
        comparison_text += f"  Exponential:   {comp['aic']['exponential']:.2f}\n"
        comparison_text += f"  ΔAIC = {comp['aic']['delta']:.2f}\n\n"

        comparison_text += "-"*50 + "\n"
        comparison_text += f"PREFERRED MODEL: {comp['preferred_model'].upper()}\n"
        comparison_text += "-"*50 + "\n\n"

        # Add fitted parameters
        if comp['preferred_model'] == 'power_law':
            params = results['fits']['power_law']['parameters']
            errs = results['fits']['power_law']['uncertainties']
            comparison_text += "Power Law Parameters:\n"
            comparison_text += f"  E_∞ = {params['E_inf']:.4f} ± {errs['E_inf_err']:.4f}\n"
            comparison_text += f"  A   = {params['A']:.6f} ± {errs['A_err']:.6f}\n"
            comparison_text += f"  α   = {params['alpha']:.4f} ± {errs['alpha_err']:.4f}\n"
        else:
            params = results['fits']['exponential']['parameters']
            errs = results['fits']['exponential']['uncertainties']
            comparison_text += "Exponential Parameters:\n"
            comparison_text += f"  E_∞ = {params['E_inf']:.4f} ± {errs['E_inf_err']:.4f}\n"
            comparison_text += f"  B   = {params['B']:.4f} ± {errs['B_err']:.4f}\n"
            comparison_text += f"  β   = {params['beta']:.2f} ± {errs['beta_err']:.2f}\n"

    ax.text(0.05, 0.95, comparison_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Figure saved: {output_path}")
    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution flow."""

    print("="*80)
    print("CYCLE 1399: FUNCTIONAL FORM FITTING")
    print("E_min vs f_spawn Relationship Characterization")
    print("="*80)
    print(f"\nTimestamp: {datetime.now().isoformat()}")

    # Load Cycle 1398 results
    print(f"\nLoading data from: {RESULTS_FILE}")
    with open(RESULTS_FILE, 'r') as f:
        cycle1398_results = json.load(f)

    # Extract E_min by f_spawn data
    e_min_by_f = cycle1398_results['statistics']['e_min_by_f_spawn']

    f_spawn_values = []
    e_min_means = []
    e_min_stds = []

    for f_str, stats in sorted(e_min_by_f.items(), key=lambda x: float(x[0])):
        f_spawn_values.append(float(f_str))
        e_min_means.append(stats['mean'])
        e_min_stds.append(stats['std'])

    print(f"Data points loaded: {len(f_spawn_values)}")

    # Fit models
    results = fit_models(f_spawn_values, e_min_means, e_min_stds)

    # Save results
    results_file = OUTPUT_DIR / 'functional_form_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved: {results_file}")

    # Create visualization
    fig_file = OUTPUT_DIR / 'e_min_functional_form_analysis.png'
    create_visualization(results, fig_file)

    print("\n" + "="*80)
    print("CYCLE 1399 COMPLETE")
    print("="*80)
    print(f"\nOutputs:")
    print(f"  - {results_file}")
    print(f"  - {fig_file}")
    print(f"\nNext steps:")
    print("  1. Validate predictions at intermediate f_spawn values (0.003, 0.006, 0.008)")
    print("  2. Test model extrapolation to boundary regions")
    print("  3. Develop theoretical mechanism for E_min(f_spawn) relationship")
    print("  4. Integrate findings into C186 manuscript")


if __name__ == '__main__':
    main()
