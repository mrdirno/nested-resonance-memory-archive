#!/usr/bin/env python3
"""
PAPER 7 PHASE 5: EIGENVALUE ANALYSIS

Purpose: Identify slow modes in V4 dynamics via Jacobian eigenvalues

Phase 4-5 discovered V4 exhibits ultra-slow drift (dN/dt ~ 0.001).
Eigenvalue analysis will reveal:
1. Number and location of fixed points
2. Stability of equilibria (Re(λ) < 0?)
3. Timescales from eigenvalues (τ = 1/|Re(λ)|)
4. Slow mode identification (near-zero eigenvalues)

Date: 2025-10-27 (Cycle 390)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, List, Optional
from scipy.optimize import fsolve
from scipy.linalg import eig
import sys

sys.path.append(str(Path(__file__).parent))

from paper7_v4_energy_threshold import NRMDynamicalSystemV4


def compute_jacobian(
    state: np.ndarray,
    params: Dict,
    R: float = 1.0
) -> np.ndarray:
    """
    Compute Jacobian matrix of V4 system at given state.

    System: dX/dt = F(X) where X = [E, N, phi, theta_rel]

    Jacobian: J_ij = ∂F_i/∂X_j

    Args:
        state: State [E, N, phi, theta_rel]
        params: V4 parameters
        R: Resource level

    Returns:
        4×4 Jacobian matrix
    """
    E, N, phi, theta_rel = state

    # Extract parameters
    r = params['r']
    K = params['K']
    alpha = params['alpha']
    beta = params['beta']
    gamma = params['gamma']
    lambda_0 = params['lambda_0']
    mu_0 = params['mu_0']
    sigma = params['sigma']
    omega = params['omega']
    kappa = params['kappa']
    phi_0 = params['phi_0']
    rho_threshold = params['rho_threshold']

    # Compute intermediate quantities
    rho = E / N if N > 0 else 0.0
    energy_gate = 1.0 / (1.0 + np.exp(-kappa * (rho - rho_threshold)))
    energy_gate_deriv = kappa * energy_gate * (1.0 - energy_gate)  # ∂g/∂ρ

    lambda_c = lambda_0 * energy_gate * phi**2
    crowding = (N / K)**2
    lambda_d = mu_0 * (1.0 + sigma * crowding)

    # Derivatives of energy_gate with respect to E and N
    if N > 0:
        dg_dE = energy_gate_deriv / N
        dg_dN = -energy_gate_deriv * E / (N**2)
    else:
        dg_dE = 0.0
        dg_dN = 0.0

    # Derivatives of lambda_c
    dlambda_c_dE = lambda_0 * phi**2 * dg_dE
    dlambda_c_dN = lambda_0 * phi**2 * dg_dN
    dlambda_c_dphi = 2.0 * lambda_0 * energy_gate * phi

    # Derivatives of lambda_d
    dlambda_d_dN = mu_0 * sigma * 2 * N / (K**2)

    # Initialize Jacobian
    J = np.zeros((4, 4))

    # Row 1: dE/dt = gamma * R - alpha * lambda_c * E - beta * N * E
    J[0, 0] = -alpha * lambda_c - alpha * E * dlambda_c_dE - beta * N
    J[0, 1] = -alpha * E * dlambda_c_dN - beta * E
    J[0, 2] = -alpha * E * dlambda_c_dphi
    J[0, 3] = 0.0

    # Row 2: dN/dt = lambda_c * N - lambda_d * N
    J[1, 0] = N * dlambda_c_dE
    J[1, 1] = lambda_c + N * dlambda_c_dN - lambda_d - N * dlambda_d_dN
    J[1, 2] = N * dlambda_c_dphi
    J[1, 3] = 0.0

    # Row 3: dphi/dt = phi_0 * r * (1 - phi) - lambda_c * phi
    J[2, 0] = -phi * dlambda_c_dE
    J[2, 1] = -phi * dlambda_c_dN
    J[2, 2] = -phi_0 * r - lambda_c - phi * dlambda_c_dphi
    J[2, 3] = 0.0

    # Row 4: d(theta_rel)/dt = -omega
    # This is constant, so Jacobian is zero
    J[3, 0] = 0.0
    J[3, 1] = 0.0
    J[3, 2] = 0.0
    J[3, 3] = 0.0

    return J


def find_fixed_point(
    initial_guess: np.ndarray,
    params: Dict,
    R: float = 1.0
) -> Optional[np.ndarray]:
    """
    Find fixed point near initial guess using Newton's method.

    Note: V4 has no true fixed point because theta_rel is always changing.
    We search for quasi-equilibria where dE/dt = dN/dt = dphi/dt = 0.

    Args:
        initial_guess: Initial state [E, N, phi, theta_rel]
        params: V4 parameters
        R: Resource level

    Returns:
        Fixed point or None if not found
    """
    model = NRMDynamicalSystemV4(params)

    def residuals(X):
        """
        Return [dE/dt, dN/dt, dphi/dt] at state X.
        Ignore theta_rel equation (always non-zero).
        """
        state = np.array([X[0], X[1], X[2], initial_guess[3]])
        dX_dt = model._derivatives(state, 0.0, lambda t: R)
        return dX_dt[:3]  # Only E, N, phi equations

    try:
        # Solve for [E, N, phi] that gives dE/dt = dN/dt = dphi/dt = 0
        X_eq = fsolve(residuals, initial_guess[:3], full_output=True)
        solution, info, ier, msg = X_eq

        if ier == 1:  # Success
            # Construct full state (keep theta_rel from initial guess)
            fixed_point = np.array([solution[0], solution[1], solution[2], initial_guess[3]])

            # Verify it's actually a fixed point
            residual_norm = np.linalg.norm(residuals(solution))
            if residual_norm < 1e-6:
                return fixed_point
            else:
                return None
        else:
            return None

    except Exception:
        return None


def analyze_eigenvalues(
    state: np.ndarray,
    params: Dict,
    R: float = 1.0
) -> Dict:
    """
    Analyze eigenvalues of Jacobian at given state.

    Args:
        state: State [E, N, phi, theta_rel]
        params: V4 parameters
        R: Resource level

    Returns:
        Eigenvalue analysis results
    """
    J = compute_jacobian(state, params, R)

    # Compute eigenvalues and eigenvectors
    eigenvalues, eigenvectors = eig(J)

    # Sort by real part (most negative first = fastest decay)
    idx = np.argsort(eigenvalues.real)
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Compute timescales (τ = 1/|Re(λ)|)
    timescales = []
    for lam in eigenvalues:
        if lam.real < 0:
            tau = -1.0 / lam.real
            timescales.append(tau)
        elif lam.real > 0:
            timescales.append(-np.inf)  # Unstable (exponential growth)
        else:
            timescales.append(np.inf)  # Neutral (marginal stability)

    timescales = np.array(timescales)

    # Identify slow modes (largest timescales)
    slow_mode_idx = np.argmax(timescales[timescales < np.inf]) if any(timescales < np.inf) else None

    # Stability: all Re(λ) < 0 except for theta_rel mode
    stable = all(eigenvalues[:3].real < 0)  # Check first 3 (E, N, phi)

    return {
        'jacobian': J,
        'eigenvalues': eigenvalues,
        'eigenvectors': eigenvectors,
        'timescales': timescales,
        'slow_mode_idx': slow_mode_idx,
        'stable': stable,
        'state': state
    }


def scan_eigenvalues_along_trajectory(
    trajectory: np.ndarray,
    t_span: np.ndarray,
    params: Dict,
    sample_interval: int = 1000
) -> Dict:
    """
    Compute eigenvalues at multiple points along trajectory.

    Args:
        trajectory: Full trajectory array
        t_span: Time points
        params: V4 parameters
        sample_interval: Sample every N points

    Returns:
        Eigenvalue evolution data
    """
    print("\\nScanning eigenvalues along trajectory...")

    sample_indices = range(0, len(trajectory), sample_interval)
    n_samples = len(sample_indices)

    t_samples = []
    eigenvalue_series = [[] for _ in range(4)]  # 4 eigenvalues
    timescale_series = [[] for _ in range(4)]

    for idx in sample_indices:
        state = trajectory[idx]
        t = t_span[idx]

        analysis = analyze_eigenvalues(state, params)

        t_samples.append(t)
        for i in range(4):
            eigenvalue_series[i].append(analysis['eigenvalues'][i])
            timescale_series[i].append(analysis['timescales'][i])

    print(f"  Sampled {n_samples} points from t={t_span[0]:.0f} to {t_span[-1]:.0f}")

    return {
        't_samples': np.array(t_samples),
        'eigenvalue_series': [np.array(ev) for ev in eigenvalue_series],
        'timescale_series': [np.array(ts) for ts in timescale_series]
    }


def eigenvalue_analysis_main(
    base_params: Dict,
    initial_state: np.ndarray,
    trajectory: np.ndarray,
    t_span: np.ndarray
) -> Dict:
    """
    Complete eigenvalue analysis.

    Args:
        base_params: V4 parameters
        initial_state: Initial state
        trajectory: Trajectory from Phase 5 simulation
        t_span: Time points

    Returns:
        Complete analysis results
    """
    print("\\n" + "=" * 70)
    print("PAPER 7 PHASE 5: EIGENVALUE ANALYSIS")
    print("=" * 70)
    print()

    # 1. Analyze initial state
    print("Analyzing initial state...")
    initial_analysis = analyze_eigenvalues(initial_state, base_params)
    print(f"  Eigenvalues: {initial_analysis['eigenvalues']}")
    print(f"  Timescales: {initial_analysis['timescales']}")
    print(f"  Stable: {initial_analysis['stable']}")

    # 2. Analyze final state
    print("\\nAnalyzing final state (t=10,000)...")
    final_state = trajectory[-1]
    final_analysis = analyze_eigenvalues(final_state, base_params)
    print(f"  State: E={final_state[0]:.2f}, N={final_state[1]:.2f}, phi={final_state[2]:.4f}, theta_rel={final_state[3]:.4f}")
    print(f"  Eigenvalues: {final_analysis['eigenvalues']}")
    print(f"  Timescales: {final_analysis['timescales']}")
    print(f"  Stable: {final_analysis['stable']}")

    # 3. Identify slow mode
    if final_analysis['slow_mode_idx'] is not None:
        slow_idx = final_analysis['slow_mode_idx']
        slow_eigenvalue = final_analysis['eigenvalues'][slow_idx]
        slow_timescale = final_analysis['timescales'][slow_idx]
        slow_eigenvector = final_analysis['eigenvectors'][:, slow_idx]

        print(f"\\nSlow mode identified:")
        print(f"  Eigenvalue: {slow_eigenvalue}")
        print(f"  Timescale: {slow_timescale:.0f}")
        print(f"  Eigenvector: {slow_eigenvector}")

    # 4. Scan along trajectory
    evolution = scan_eigenvalues_along_trajectory(trajectory, t_span, base_params, sample_interval=1000)

    # 5. Search for fixed point near final state
    print("\\nSearching for quasi-equilibrium...")
    fixed_point = find_fixed_point(final_state, base_params)

    if fixed_point is not None:
        print(f"  ✅ Quasi-equilibrium found:")
        print(f"     E_eq = {fixed_point[0]:.2f}")
        print(f"     N_eq = {fixed_point[1]:.2f}")
        print(f"     phi_eq = {fixed_point[2]:.4f}")

        # Analyze equilibrium
        eq_analysis = analyze_eigenvalues(fixed_point, base_params)
        print(f"     Eigenvalues: {eq_analysis['eigenvalues']}")
        print(f"     Stable: {eq_analysis['stable']}")
    else:
        print(f"  ❌ No quasi-equilibrium found near final state")

    return {
        'initial': initial_analysis,
        'final': final_analysis,
        'evolution': evolution,
        'fixed_point': fixed_point,
        'fixed_point_analysis': eq_analysis if fixed_point is not None else None
    }


def plot_eigenvalue_analysis(results: Dict, output_dir: Path):
    """
    Visualize eigenvalue analysis results.

    Args:
        results: Analysis results
        output_dir: Output directory
    """
    print("\\nGenerating eigenvalue analysis figure...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    evolution = results['evolution']
    t = evolution['t_samples']

    # Panel 1: Real parts of eigenvalues vs time
    ax = axes[0, 0]
    for i in range(4):
        ev_real = [ev.real for ev in evolution['eigenvalue_series'][i]]
        ax.plot(t, ev_real, 'o-', markersize=4, label=f'λ{i+1}')
    ax.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Re(λ)', fontsize=11)
    ax.set_title('Eigenvalue Real Parts Evolution', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Panel 2: Imaginary parts of eigenvalues vs time
    ax = axes[0, 1]
    for i in range(4):
        ev_imag = [ev.imag for ev in evolution['eigenvalue_series'][i]]
        ax.plot(t, ev_imag, 'o-', markersize=4, label=f'λ{i+1}')
    ax.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Im(λ)', fontsize=11)
    ax.set_title('Eigenvalue Imaginary Parts Evolution', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Panel 3: Timescales vs time
    ax = axes[1, 0]
    for i in range(4):
        ts = evolution['timescale_series'][i]
        # Filter out infinities and negatives for plotting
        ts_plot = np.where((ts > 0) & (ts < 1e6), ts, np.nan)
        ax.plot(t, ts_plot, 'o-', markersize=4, label=f'τ{i+1}')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Timescale (τ = 1/|Re(λ)|)', fontsize=11)
    ax.set_title('Timescale Evolution', fontsize=12, fontweight='bold')
    ax.set_yscale('log')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Panel 4: Eigenvalue spectrum at final state
    ax = axes[1, 1]
    final = results['final']
    eigenvalues = final['eigenvalues']

    ax.plot(eigenvalues.real, eigenvalues.imag, 'ro', markersize=12, label='Final state')

    if results['fixed_point_analysis']:
        eq_eigenvalues = results['fixed_point_analysis']['eigenvalues']
        ax.plot(eq_eigenvalues.real, eq_eigenvalues.imag, 'bs', markersize=12, label='Equilibrium')

    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5)
    ax.axvline(0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Re(λ)', fontsize=11)
    ax.set_ylabel('Im(λ)', fontsize=11)
    ax.set_title('Eigenvalue Spectrum (Complex Plane)', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Add annotations for final state eigenvalues
    for i, lam in enumerate(eigenvalues):
        ax.annotate(f'λ{i+1}', (lam.real, lam.imag), fontsize=8,
                   xytext=(5, 5), textcoords='offset points')

    fig.suptitle('Paper 7 Phase 5: Eigenvalue Analysis',
                fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = output_dir / f"paper7_phase5_eigenvalue_analysis_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def main():
    """Main execution: eigenvalue analysis."""
    print("\\nLoading Phase 5 timescale results...")

    # Use same parameters as timescale quantification
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

    # Simulate (reuse from timescale quantification)
    model = NRMDynamicalSystemV4(base_params)
    t_span = np.arange(0, 10000.1, 0.1)
    R_func = lambda t: 1.0
    trajectory = model.simulate(t_span, initial_state, R_func)

    # Run eigenvalue analysis
    results = eigenvalue_analysis_main(base_params, initial_state, trajectory, t_span)

    # Visualize
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_eigenvalue_analysis(results, output_dir)

    # Summary
    print("\\n" + "=" * 70)
    print("EIGENVALUE ANALYSIS SUMMARY")
    print("=" * 70)
    print()

    final = results['final']
    print("Final state eigenvalues:")
    for i, (lam, tau) in enumerate(zip(final['eigenvalues'], final['timescales'])):
        stability = "stable" if lam.real < 0 else "unstable"
        print(f"  λ{i+1} = {lam:.4e} → τ{i+1} = {tau:.2e} ({stability})")

    if results['fixed_point']:
        print(f"\\nQuasi-equilibrium found:")
        fp = results['fixed_point']
        print(f"  E_eq = {fp[0]:.2f}, N_eq = {fp[1]:.2f}, phi_eq = {fp[2]:.4f}")
    else:
        print(f"\\nNo quasi-equilibrium found")

    print()


if __name__ == "__main__":
    main()
