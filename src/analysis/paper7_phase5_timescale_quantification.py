#!/usr/bin/env python3
"""
PAPER 7 PHASE 5: TIMESCALE QUANTIFICATION

Purpose: Quantify the three temporal regimes discovered in Phase 4

Phase 4 discovered V4 has three timescales:
1. Fast transient (t=0-500): τ_fast ~ 100-200
2. Medium fluctuations (t=500-1500): τ_medium ~ 500-1000, CV = 15.2%
3. Slow drift (t=1500-5000+): τ_slow ~ 2000+, CV = 1.0%

Phase 5 Goals:
1. Fit exponential decay model to CV(t)
2. Extract τ_medium and τ_slow quantitatively
3. Identify crossover time where CV(t) = empirical 9.2%
4. Characterize drift rate in slow regime

Date: 2025-10-27 (Cycle 390)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, List
from scipy.optimize import curve_fit
from scipy.stats import linregress
import sys

sys.path.append(str(Path(__file__).parent))

from paper7_v4_energy_threshold import NRMDynamicalSystemV4


def simulate_v4_extended(
    model: NRMDynamicalSystemV4,
    initial_state: np.ndarray,
    t_total: float = 10000.0,
    dt: float = 0.1,
    R_value: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate V4 for extended time to capture all timescales.

    Args:
        model: V4 model instance
        initial_state: Initial [E, N, phi, theta_rel]
        t_total: Total simulation time (default 10,000)
        dt: Time step
        R_value: Resource level

    Returns:
        (t_span, trajectory) arrays
    """
    print(f"  Simulating V4 for {t_total} time units...")

    t_span = np.arange(0, t_total + dt, dt)
    R_func = lambda t: R_value

    trajectory = model.simulate(t_span, initial_state, R_func)

    print(f"  Final state: N = {trajectory[-1, 1]:.2f}, E = {trajectory[-1, 0]:.2f}")

    return t_span, trajectory


def calculate_cv_timeseries(
    trajectory: np.ndarray,
    t_span: np.ndarray,
    window_size: float = 100.0,
    step_size: float = 50.0,
    transient_cutoff: float = 500.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate CV as a function of time using sliding windows.

    Args:
        trajectory: Full trajectory array
        t_span: Time points
        window_size: Window for calculating local statistics
        step_size: Step between windows
        transient_cutoff: Exclude t < transient_cutoff from analysis

    Returns:
        (t_centers, cv_values, mean_values, std_values)
    """
    dt = t_span[1] - t_span[0]
    window_indices = int(window_size / dt)
    step_indices = int(step_size / dt)

    # Start after transient
    start_idx = int(transient_cutoff / dt)
    N_data = trajectory[start_idx:, 1]
    t_data = t_span[start_idx:]

    t_centers = []
    cv_values = []
    mean_values = []
    std_values = []

    for i in range(0, len(N_data) - window_indices, step_indices):
        window = N_data[i:i+window_indices]
        t_center = t_data[i + window_indices // 2]

        mean_N = np.mean(window)
        std_N = np.std(window)
        cv = std_N / mean_N if mean_N > 0 else 0.0

        t_centers.append(t_center)
        cv_values.append(cv)
        mean_values.append(mean_N)
        std_values.append(std_N)

    return (np.array(t_centers), np.array(cv_values),
            np.array(mean_values), np.array(std_values))


def fit_exponential_decay(
    t: np.ndarray,
    cv: np.ndarray,
    model: str = 'double'
) -> Dict:
    """
    Fit exponential decay model to CV(t).

    Models:
        'single': CV(t) = CV_inf + A * exp(-t/τ)
        'double': CV(t) = CV_inf + A1 * exp(-t/τ1) + A2 * exp(-t/τ2)

    Args:
        t: Time values
        cv: CV values
        model: 'single' or 'double' exponential

    Returns:
        Fit results dictionary
    """
    if model == 'single':
        # Single exponential: CV(t) = CV_inf + A * exp(-t/tau)
        def func(t, cv_inf, A, tau):
            return cv_inf + A * np.exp(-t / tau)

        # Initial guess
        p0 = [0.01, 0.14, 1000.0]  # cv_inf, A, tau
        bounds = ([0, 0, 100], [0.2, 1.0, 10000])

        try:
            popt, pcov = curve_fit(func, t, cv, p0=p0, bounds=bounds, maxfev=10000)
            perr = np.sqrt(np.diag(pcov))

            cv_fit = func(t, *popt)
            residuals = cv - cv_fit
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((cv - np.mean(cv))**2)
            r_squared = 1 - (ss_res / ss_tot)

            return {
                'model': 'single',
                'cv_inf': popt[0],
                'cv_inf_err': perr[0],
                'A': popt[1],
                'A_err': perr[1],
                'tau': popt[2],
                'tau_err': perr[2],
                'r_squared': r_squared,
                'cv_fit': cv_fit
            }
        except RuntimeError:
            return None

    elif model == 'double':
        # Double exponential: CV(t) = CV_inf + A1*exp(-t/tau1) + A2*exp(-t/tau2)
        def func(t, cv_inf, A1, tau1, A2, tau2):
            return cv_inf + A1 * np.exp(-t / tau1) + A2 * np.exp(-t / tau2)

        # Initial guess: fast + slow components
        p0 = [0.01, 0.05, 500.0, 0.09, 2000.0]  # cv_inf, A1, tau1, A2, tau2
        bounds = ([0, 0, 100, 0, 1000], [0.2, 0.5, 2000, 0.5, 10000])

        try:
            popt, pcov = curve_fit(func, t, cv, p0=p0, bounds=bounds, maxfev=10000)
            perr = np.sqrt(np.diag(pcov))

            cv_fit = func(t, *popt)
            residuals = cv - cv_fit
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((cv - np.mean(cv))**2)
            r_squared = 1 - (ss_res / ss_tot)

            return {
                'model': 'double',
                'cv_inf': popt[0],
                'cv_inf_err': perr[0],
                'A1': popt[1],
                'A1_err': perr[1],
                'tau1': popt[2],
                'tau1_err': perr[2],
                'A2': popt[3],
                'A2_err': perr[3],
                'tau2': popt[4],
                'tau2_err': perr[4],
                'r_squared': r_squared,
                'cv_fit': cv_fit
            }
        except RuntimeError:
            return None

    else:
        raise ValueError(f"Unknown model: {model}")


def find_crossover_time(
    t: np.ndarray,
    cv: np.ndarray,
    target_cv: float = 0.092
) -> Dict:
    """
    Find time when CV(t) crosses target empirical value.

    Args:
        t: Time values
        cv: CV values
        target_cv: Target CV from Paper 2

    Returns:
        Crossover analysis results
    """
    # Find where CV crosses target (interpolate)
    if cv[0] < target_cv or cv[-1] > target_cv:
        # CV doesn't cross target in available data
        return {
            'crossover_time': None,
            'crossover_cv': None,
            'crossed': False,
            'reason': 'CV does not cross target in simulation window'
        }

    # Find crossing point (CV decreasing from above)
    idx = np.where(cv <= target_cv)[0]
    if len(idx) == 0:
        return {
            'crossover_time': None,
            'crossover_cv': None,
            'crossed': False,
            'reason': 'CV never reaches target'
        }

    cross_idx = idx[0]

    # Linear interpolation for better accuracy
    if cross_idx > 0:
        t1, t2 = t[cross_idx-1], t[cross_idx]
        cv1, cv2 = cv[cross_idx-1], cv[cross_idx]

        # Interpolate: t_cross = t1 + (target - cv1) * (t2 - t1) / (cv2 - cv1)
        t_cross = t1 + (target_cv - cv1) * (t2 - t1) / (cv2 - cv1)
        cv_cross = target_cv
    else:
        t_cross = t[cross_idx]
        cv_cross = cv[cross_idx]

    return {
        'crossover_time': t_cross,
        'crossover_cv': cv_cross,
        'crossed': True,
        'reason': 'Crossover found'
    }


def analyze_drift_rate(
    trajectory: np.ndarray,
    t_span: np.ndarray,
    drift_start: float = 2000.0,
    drift_end: float = 10000.0
) -> Dict:
    """
    Analyze population drift rate in slow regime.

    Args:
        trajectory: Full trajectory
        t_span: Time points
        drift_start: Start of drift regime
        drift_end: End of drift regime

    Returns:
        Drift analysis results
    """
    dt = t_span[1] - t_span[0]
    start_idx = int(drift_start / dt)
    end_idx = int(drift_end / dt)

    t_drift = t_span[start_idx:end_idx]
    N_drift = trajectory[start_idx:end_idx, 1]

    # Linear regression
    slope, intercept, r_value, p_value, std_err = linregress(t_drift, N_drift)

    return {
        'drift_rate': slope,  # dN/dt
        'drift_rate_err': std_err,
        'r_squared': r_value**2,
        'p_value': p_value,
        'N_start': N_drift[0],
        'N_end': N_drift[-1],
        'delta_N': N_drift[-1] - N_drift[0],
        'time_range': (drift_start, drift_end)
    }


def quantify_timescales(
    base_params: Dict,
    initial_state: np.ndarray,
    empirical_cv: float = 0.092
) -> Dict:
    """
    Main analysis: quantify all three timescales.

    Args:
        base_params: V4 parameters
        initial_state: Initial state
        empirical_cv: Target CV from Paper 2

    Returns:
        Complete timescale analysis
    """
    print("\\n" + "=" * 70)
    print("PAPER 7 PHASE 5: TIMESCALE QUANTIFICATION")
    print("=" * 70)
    print()

    # Create model
    model = NRMDynamicalSystemV4(base_params)

    # Simulate extended time
    t_span, trajectory = simulate_v4_extended(model, initial_state, t_total=10000.0)

    # Calculate CV timeseries
    print("\\nCalculating CV timeseries...")
    t_cv, cv_values, mean_N, std_N = calculate_cv_timeseries(
        trajectory, t_span, window_size=100.0, step_size=50.0
    )
    print(f"  CV timeseries: {len(t_cv)} points from t={t_cv[0]:.0f} to {t_cv[-1]:.0f}")

    # Fit exponential models
    print("\\nFitting exponential decay models...")

    single_fit = fit_exponential_decay(t_cv, cv_values, model='single')
    if single_fit:
        print(f"\\n  Single exponential fit:")
        print(f"    CV_inf = {single_fit['cv_inf']:.4f} ± {single_fit['cv_inf_err']:.4f}")
        print(f"    A = {single_fit['A']:.4f} ± {single_fit['A_err']:.4f}")
        print(f"    τ = {single_fit['tau']:.0f} ± {single_fit['tau_err']:.0f}")
        print(f"    R² = {single_fit['r_squared']:.4f}")

    double_fit = fit_exponential_decay(t_cv, cv_values, model='double')
    if double_fit:
        print(f"\\n  Double exponential fit:")
        print(f"    CV_inf = {double_fit['cv_inf']:.4f} ± {double_fit['cv_inf_err']:.4f}")
        print(f"    A1 = {double_fit['A1']:.4f} ± {double_fit['A1_err']:.4f}, τ1 = {double_fit['tau1']:.0f} ± {double_fit['tau1_err']:.0f}")
        print(f"    A2 = {double_fit['A2']:.4f} ± {double_fit['A2_err']:.4f}, τ2 = {double_fit['tau2']:.0f} ± {double_fit['tau2_err']:.0f}")
        print(f"    R² = {double_fit['r_squared']:.4f}")

    # Find crossover time
    print(f"\\nFinding crossover time (CV = {empirical_cv:.3f})...")
    crossover = find_crossover_time(t_cv, cv_values, target_cv=empirical_cv)

    if crossover['crossed']:
        print(f"  ✅ Crossover found at t = {crossover['crossover_time']:.0f}")
    else:
        print(f"  ❌ {crossover['reason']}")

    # Analyze drift
    print("\\nAnalyzing drift rate (slow regime)...")
    drift = analyze_drift_rate(trajectory, t_span, drift_start=2000.0)
    print(f"  dN/dt = {drift['drift_rate']:.5f} ± {drift['drift_rate_err']:.5f}")
    print(f"  ΔN = {drift['delta_N']:.2f} (from {drift['N_start']:.2f} to {drift['N_end']:.2f})")
    print(f"  R² = {drift['r_squared']:.4f}, p = {drift['p_value']:.2e}")

    results = {
        't_span': t_span,
        'trajectory': trajectory,
        't_cv': t_cv,
        'cv_values': cv_values,
        'mean_N': mean_N,
        'std_N': std_N,
        'single_fit': single_fit,
        'double_fit': double_fit,
        'crossover': crossover,
        'drift': drift,
        'empirical_cv': empirical_cv
    }

    return results


def plot_timescale_analysis(results: Dict, output_dir: Path):
    """
    Visualize timescale quantification results.

    Args:
        results: Analysis results
        output_dir: Output directory
    """
    print("\\nGenerating timescale analysis figure...")

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # Panel 1: Full population trajectory
    ax1 = fig.add_subplot(gs[0, :])
    t = results['t_span']
    N = results['trajectory'][:, 1]
    ax1.plot(t, N, 'k-', linewidth=0.5, alpha=0.7)
    ax1.axvline(500, color='red', linestyle='--', alpha=0.5, label='Transient end')
    ax1.axvline(1500, color='orange', linestyle='--', alpha=0.5, label='Medium→Slow')
    ax1.set_xlabel('Time', fontsize=11)
    ax1.set_ylabel('Population (N)', fontsize=11)
    ax1.set_title('V4 Population Trajectory (t = 0 to 10,000)', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(alpha=0.3)

    # Panel 2: CV timeseries with fits
    ax2 = fig.add_subplot(gs[1, :])
    t_cv = results['t_cv']
    cv = results['cv_values']
    empirical_cv = results['empirical_cv']

    ax2.plot(t_cv, cv, 'o', markersize=4, alpha=0.6, label='Observed CV(t)')

    if results['single_fit']:
        ax2.plot(t_cv, results['single_fit']['cv_fit'], 'b-', linewidth=2,
                label=f"Single exp (τ={results['single_fit']['tau']:.0f}, R²={results['single_fit']['r_squared']:.3f})")

    if results['double_fit']:
        ax2.plot(t_cv, results['double_fit']['cv_fit'], 'r-', linewidth=2,
                label=f"Double exp (τ₁={results['double_fit']['tau1']:.0f}, τ₂={results['double_fit']['tau2']:.0f}, R²={results['double_fit']['r_squared']:.3f})")

    ax2.axhline(empirical_cv, color='green', linestyle='--', linewidth=2,
               label=f'Paper 2 empirical = {empirical_cv:.3f}')

    if results['crossover']['crossed']:
        t_cross = results['crossover']['crossover_time']
        ax2.axvline(t_cross, color='purple', linestyle=':', linewidth=2,
                   label=f'Crossover t = {t_cross:.0f}')
        ax2.plot(t_cross, empirical_cv, 'purple', marker='*', markersize=15)

    ax2.set_xlabel('Time', fontsize=11)
    ax2.set_ylabel('Coefficient of Variation', fontsize=11)
    ax2.set_title('CV(t) Decay and Exponential Fits', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(alpha=0.3)
    ax2.set_ylim(0, max(cv) * 1.1)

    # Panel 3: Mean population evolution
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.plot(t_cv, results['mean_N'], 'k-', linewidth=2)
    ax3.set_xlabel('Time', fontsize=11)
    ax3.set_ylabel('Mean N (100-unit windows)', fontsize=11)
    ax3.set_title('Population Mean Evolution', fontsize=12, fontweight='bold')
    ax3.grid(alpha=0.3)

    # Panel 4: Drift rate (slow regime)
    ax4 = fig.add_subplot(gs[2, 1])
    drift_start = results['drift']['time_range'][0]
    drift_end = results['drift']['time_range'][1]

    dt = t[1] - t[0]
    start_idx = int(drift_start / dt)
    end_idx = int(drift_end / dt)

    t_drift = t[start_idx:end_idx]
    N_drift = N[start_idx:end_idx]

    ax4.plot(t_drift, N_drift, 'k-', linewidth=0.5, alpha=0.7, label='Population')

    # Linear fit
    slope = results['drift']['drift_rate']
    intercept = N_drift[0] - slope * t_drift[0]
    N_fit = slope * t_drift + intercept
    ax4.plot(t_drift, N_fit, 'r--', linewidth=2,
            label=f"dN/dt = {slope:.5f} ± {results['drift']['drift_rate_err']:.5f}")

    ax4.set_xlabel('Time', fontsize=11)
    ax4.set_ylabel('Population (N)', fontsize=11)
    ax4.set_title(f"Slow Drift (t = {drift_start:.0f} to {drift_end:.0f})",
                 fontsize=12, fontweight='bold')
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(alpha=0.3)

    fig.suptitle('Paper 7 Phase 5: Timescale Quantification',
                fontsize=14, fontweight='bold', y=0.995)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = output_dir / f"paper7_phase5_timescale_quantification_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def main():
    """Main execution: quantify V4 timescales."""

    # V4 sustained parameters
    base_params = {
        'r': 0.15,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 2.5,
        'mu_0': 0.4,
        'sigma': 0.1,
        'omega': 0.02,
        'kappa': 0.1,
        'phi_0': 0.06,
        'rho_threshold': 5.0
    }

    initial_state = np.array([100.0, 10.0, 0.5, 0.0])
    empirical_cv = 0.092

    # Run analysis
    results = quantify_timescales(base_params, initial_state, empirical_cv)

    # Visualize
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_timescale_analysis(results, output_dir)

    # Summary
    print("\\n" + "=" * 70)
    print("TIMESCALE QUANTIFICATION SUMMARY")
    print("=" * 70)
    print()

    if results['double_fit']:
        print("Three Temporal Regimes Quantified:")
        print(f"  1. Fast transient: t < 500")
        print(f"  2. Medium fluctuations: τ₁ = {results['double_fit']['tau1']:.0f} ± {results['double_fit']['tau1_err']:.0f}")
        print(f"  3. Slow drift: τ₂ = {results['double_fit']['tau2']:.0f} ± {results['double_fit']['tau2_err']:.0f}")
        print()
        print(f"Asymptotic CV: {results['double_fit']['cv_inf']:.4f} ± {results['double_fit']['cv_inf_err']:.4f}")

    if results['crossover']['crossed']:
        print(f"\\nCrossover to empirical CV (9.2%): t = {results['crossover']['crossover_time']:.0f}")

    print(f"\\nDrift rate: {results['drift']['drift_rate']:.5f} ± {results['drift']['drift_rate_err']:.5f} N/time unit")
    print(f"Population change (t=2000-10000): {results['drift']['N_start']:.2f} → {results['drift']['N_end']:.2f}")
    print()


if __name__ == "__main__":
    main()
