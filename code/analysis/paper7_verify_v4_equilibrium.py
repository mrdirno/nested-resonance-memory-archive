#!/usr/bin/env python3
"""
Paper 7: Verify V4 Deterministic Equilibrium

Purpose: Test if V4 reaches true equilibrium at extended timescales (t=100,000).
         Phase 5 showed dN/dt = 0.00093 at t=10,000 (not zero), suggesting slow drift.
         Phase 6 CLE showed extinction even from "steady state" at N=215.

Question: Does V4 have a true stable equilibrium with N >> 1?

Method: Run V4 deterministic (no noise) for t=100,000 and measure:
        - Final state (E, N, φ, θ)
        - Drift rates (dE/dt, dN/dt, dφ/dt, dθ/dt)
        - Convergence to equilibrium (exponential approach?)

Date: 2025-10-27 (Cycle 391)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.integrate import odeint
from typing import Dict, Tuple
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))


def ode_system_v4(state: np.ndarray, t: float, params: Dict, R_func: callable) -> np.ndarray:
    """
    V4 dynamics (deterministic).

    State: [E_total, N, phi, theta_rel]
    """
    E_total, N, phi, theta_rel = state

    # Enforce constraints
    N = max(1.0, N)
    E_total = max(0.0, E_total)
    phi = np.clip(phi, 0.0, 1.0)

    # Energy density
    rho = E_total / N

    # Parameters
    r = params['r']
    alpha = params['alpha']
    beta = params['beta']
    gamma = params['gamma']
    lambda_0 = params['lambda_0']
    mu_0 = params['mu_0']
    sigma = params['sigma']
    omega = params['omega']
    phi_0 = params.get('phi_0', 0.06)
    rho_threshold = params.get('rho_threshold', 5.0)
    kappa = params.get('kappa', 0.1)
    K = params['K']

    # Reality input
    R = R_func(t)

    # Energy gate
    energy_gate = 1.0 / (1.0 + np.exp(-kappa * (rho - rho_threshold)))

    # Resonance factor
    R_resonance = R * np.cos(theta_rel)

    # Composition rate
    lambda_c = lambda_0 * energy_gate * phi**2

    # Death rate (density-dependent)
    death_rate = mu_0 * (1 + sigma * (N / K))

    # Derivatives
    dE_dt = gamma * R - alpha * lambda_c * E_total - beta * N * E_total
    dN_dt = (lambda_c - death_rate) * N
    dphi_dt = phi_0 * r * (1 - phi) - lambda_c * phi
    dtheta_dt = -omega

    return np.array([dE_dt, dN_dt, dphi_dt, dtheta_dt])


def run_extended_simulation(params: Dict, initial_state: np.ndarray,
                            t_max: float = 100000, dt: float = 1.0) -> Dict:
    """
    Run V4 deterministic for extended time to verify equilibrium.

    Args:
        params: V4 model parameters
        initial_state: Starting state [E, N, phi, theta]
        t_max: Maximum simulation time
        dt: Output timestep

    Returns:
        Dictionary with trajectory and equilibrium analysis
    """
    print(f"\nRunning V4 deterministic simulation to t={t_max:,.0f}...")
    print(f"Initial state: E={initial_state[0]:.2f}, N={initial_state[1]:.2f}, φ={initial_state[2]:.4f}")

    # Reality input (constant)
    R_func = lambda t: 1.0

    # Time points
    t_span = np.arange(0, t_max + dt, dt)
    n_points = len(t_span)

    # Integrate
    print(f"Integrating {n_points:,} timesteps...")
    trajectory = odeint(ode_system_v4, initial_state, t_span, args=(params, R_func))

    # Extract variables
    E = trajectory[:, 0]
    N = trajectory[:, 1]
    phi = trajectory[:, 2]
    theta = trajectory[:, 3]

    # Compute derivatives at final point
    final_state = trajectory[-1]
    final_derivs = ode_system_v4(final_state, t_span[-1], params, R_func)

    # Measure convergence by looking at final 10% of trajectory
    final_window = int(0.1 * n_points)
    final_mean_N = np.mean(N[-final_window:])
    final_std_N = np.std(N[-final_window:])
    final_drift_N = (N[-1] - N[-final_window]) / (t_span[-1] - t_span[-final_window])

    # Check if system is at equilibrium
    drift_threshold = 1e-6  # Consider equilibrium if |dX/dt| < threshold
    at_equilibrium = all(abs(final_derivs) < drift_threshold)

    print(f"\n{'='*70}")
    print("EQUILIBRIUM ANALYSIS")
    print(f"{'='*70}")
    print(f"\nFinal State (t={t_max:,.0f}):")
    print(f"  E = {final_state[0]:.4f}")
    print(f"  N = {final_state[1]:.4f}")
    print(f"  φ = {final_state[2]:.4f}")
    print(f"  θ = {final_state[3]:.4f}")

    print(f"\nFinal Derivatives (rates of change):")
    print(f"  dE/dt = {final_derivs[0]:.6e}")
    print(f"  dN/dt = {final_derivs[1]:.6e}")
    print(f"  dφ/dt = {final_derivs[2]:.6e}")
    print(f"  dθ/dt = {final_derivs[3]:.6e}")

    print(f"\nFinal Window Statistics (last 10% of trajectory):")
    print(f"  Mean N: {final_mean_N:.4f} ± {final_std_N:.4f}")
    print(f"  Drift rate: {final_drift_N:.6e} per unit time")

    print(f"\nEquilibrium Status:")
    if at_equilibrium:
        print(f"  ✅ EQUILIBRIUM REACHED (all |dX/dt| < {drift_threshold:.0e})")
    else:
        print(f"  ❌ NOT AT EQUILIBRIUM (some |dX/dt| > {drift_threshold:.0e})")
        print(f"     Largest drift: {max(abs(final_derivs)):.6e}")

    # Compare to Phase 5 state at t=10,000
    phase5_state = np.array([2411.77, 215.30, 0.6074, 0.0])
    print(f"\nComparison to Phase 5 (t=10,000):")
    print(f"  E: {phase5_state[0]:.2f} → {final_state[0]:.2f} (Δ={final_state[0]-phase5_state[0]:+.2f})")
    print(f"  N: {phase5_state[1]:.2f} → {final_state[1]:.2f} (Δ={final_state[1]-phase5_state[1]:+.2f})")
    print(f"  φ: {phase5_state[2]:.4f} → {final_state[2]:.4f} (Δ={final_state[2]-phase5_state[2]:+.4f})")

    return {
        't_span': t_span,
        'trajectory': trajectory,
        'final_state': final_state,
        'final_derivs': final_derivs,
        'at_equilibrium': at_equilibrium,
        'final_mean_N': final_mean_N,
        'final_std_N': final_std_N,
        'final_drift_N': final_drift_N,
        'phase5_comparison': {
            'phase5_N': phase5_state[1],
            'final_N': final_state[1],
            'delta_N': final_state[1] - phase5_state[1]
        }
    }


def generate_figure(results: Dict, output_dir: Path):
    """
    Generate 4-panel diagnostic figure.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Paper 7: V4 Deterministic Equilibrium Verification (t=100,000)",
                fontsize=14, fontweight='bold')

    t = results['t_span']
    traj = results['trajectory']

    # Panel A: Population over time
    ax = axes[0, 0]
    ax.plot(t, traj[:, 1], 'b-', lw=1.5)
    ax.axhline(215.30, color='r', linestyle='--', label='Phase 5 (t=10k)', lw=2)
    ax.axhline(results['final_state'][1], color='g', linestyle='--',
               label=f'Final (t=100k): N={results["final_state"][1]:.2f}', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('A) Population Trajectory', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel B: Population zoom (last 10%)
    ax = axes[0, 1]
    final_window = int(0.1 * len(t))
    t_final = t[-final_window:]
    N_final = traj[-final_window:, 1]
    ax.plot(t_final, N_final, 'b-', lw=1.5)
    ax.axhline(results['final_mean_N'], color='r', linestyle='--',
               label=f'Mean: {results["final_mean_N"]:.2f}', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('B) Final 10% Window (Zoom)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel C: Energy and resonance
    ax = axes[1, 0]
    ax.plot(t, traj[:, 0], 'r-', label='Energy E', lw=1.5)
    ax.set_xlabel('Time')
    ax.set_ylabel('Energy E', color='r')
    ax.tick_params(axis='y', labelcolor='r')
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3)

    ax2 = ax.twinx()
    ax2.plot(t, traj[:, 2], 'g-', label='Resonance φ', lw=1.5)
    ax2.set_ylabel('Resonance φ', color='g')
    ax2.tick_params(axis='y', labelcolor='g')
    ax2.legend(loc='upper right')
    ax.set_title('C) Energy and Resonance', fontweight='bold')

    # Panel D: Drift rates
    ax = axes[1, 1]
    derivs_labels = ['dE/dt', 'dN/dt', 'dφ/dt']
    derivs_values = [results['final_derivs'][i] for i in range(3)]
    colors = ['red', 'blue', 'green']

    bars = ax.bar(derivs_labels, np.abs(derivs_values), color=colors, alpha=0.7)
    ax.axhline(1e-6, color='k', linestyle='--', label='Equilibrium threshold', lw=2)
    ax.set_ylabel('|Derivative| (absolute value)')
    ax.set_yscale('log')
    ax.set_title('D) Final Drift Rates (log scale)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3, axis='y')

    # Add values as text
    for i, (bar, val) in enumerate(zip(bars, derivs_values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height*1.5,
                f'{val:.2e}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()

    output_path = output_dir / f"paper7_v4_equilibrium_verification_{timestamp}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Figure saved: {output_path}")
    plt.close()


def main():
    """
    Main execution: Verify V4 equilibrium at extended timescales.
    """
    print("="*70)
    print("PAPER 7: V4 DETERMINISTIC EQUILIBRIUM VERIFICATION")
    print("="*70)
    print("\nQuestion: Does V4 reach true equilibrium at t=100,000?")
    print("Context: Phase 5 showed dN/dt=0.00093 at t=10,000 (not zero)")
    print("         Phase 6 CLE showed extinction from N=215 'steady state'")
    print("         Need to verify if equilibrium exists before blaming stochasticity")

    # V4 sustained parameters (from Phase 3-5)
    params = {
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

    # Initial state (low population to test from scratch)
    initial_state = np.array([100.0, 10.0, 0.5, 0.0])  # [E, N, phi, theta]

    # Run extended simulation
    results = run_extended_simulation(params, initial_state, t_max=100000, dt=10.0)

    # Generate figure
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_figure(results, output_dir)

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = results_dir / f"paper7_v4_equilibrium_verification_{timestamp}.json"

    results_data = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'purpose': 'Verify V4 deterministic equilibrium at t=100,000',
            'params': params,
            'initial_state': initial_state.tolist()
        },
        'final_state': {
            'E': float(results['final_state'][0]),
            'N': float(results['final_state'][1]),
            'phi': float(results['final_state'][2]),
            'theta': float(results['final_state'][3])
        },
        'final_derivatives': {
            'dE_dt': float(results['final_derivs'][0]),
            'dN_dt': float(results['final_derivs'][1]),
            'dphi_dt': float(results['final_derivs'][2]),
            'dtheta_dt': float(results['final_derivs'][3])
        },
        'equilibrium_analysis': {
            'at_equilibrium': bool(results['at_equilibrium']),
            'final_mean_N': float(results['final_mean_N']),
            'final_std_N': float(results['final_std_N']),
            'final_drift_N': float(results['final_drift_N'])
        },
        'phase5_comparison': {
            'phase5_N_at_t10k': 215.30,
            'final_N_at_t100k': float(results['final_state'][1]),
            'delta_N': float(results['phase5_comparison']['delta_N']),
            'interpretation': 'Positive delta means growth, negative means collapse'
        }
    }

    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)

    print(f"\n✅ Results saved: {results_path}")

    # Final interpretation
    print(f"\n{'='*70}")
    print("INTERPRETATION")
    print(f"{'='*70}")

    if results['at_equilibrium']:
        print("\n✅ V4 HAS STABLE EQUILIBRIUM")
        print(f"   Equilibrium state: N = {results['final_state'][1]:.2f}")
        print(f"   Phase 6 CLE extinction is likely:")
        print(f"   - Stochastic instability (noise destabilizes equilibrium)")
        print(f"   - Numerical artifact (timestep too large)")
        print(f"   - Absorbing barrier (N=1 trap)")
    else:
        print("\n❌ V4 DOES NOT HAVE STABLE EQUILIBRIUM")
        print(f"   Final state still drifting: dN/dt = {results['final_derivs'][1]:.6e}")
        print(f"   Phase 6 CLE extinction is expected:")
        print(f"   - V4 model fundamentally unstable")
        print(f"   - Need V5 with explicit stability mechanism (Allee effect, spatial structure)")

        if results['final_state'][1] < 10:
            print(f"   WARNING: Population collapsed to N = {results['final_state'][1]:.2f}")
            print(f"            V4 cannot sustain populations even deterministically!")
        elif results['final_derivs'][1] < 0:
            print(f"   WARNING: Population still declining (dN/dt < 0)")
            print(f"            System slowly collapsing to absorbing barrier")

    print(f"\n{'='*70}")
    print("EQUILIBRIUM VERIFICATION COMPLETE")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
