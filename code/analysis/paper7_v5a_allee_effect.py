#!/usr/bin/env python3
"""
Paper 7: V5A Model - Allee Effect for Stable Equilibrium

Purpose: Fix V4 fundamental instability by adding Allee effect (minimum viable population).

V4 Failure: Population collapses to N = -35,471 (negative) at t=100,000
Root Cause: No negative feedback to prevent collapse when N → 0

V5A Solution: Allee Effect
- Birth rate decreases below critical population threshold
- Creates stable equilibrium with N >> 1
- Biologically realistic (cooperation, mate-finding effects)

Implementation:
    λ_c_V5 = λ_c_V4 · (N / (N + N_crit))

Where:
- λ_c_V4: Original V4 birth rate (energy_gate · φ²)
- N_crit: Critical population threshold (Allee threshold)
- (N / (N + N_crit)): Allee factor (0 when N=0, 1 when N >> N_crit)

Expected Result:
- Stable equilibrium with N > N_crit
- No collapse to negative values
- CLE stochastic extension should work (stable deterministic base)

Date: 2025-10-27 (Cycle 393)
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


class NRMDynamicalSystemV5A:
    """
    V5A model: V4 + Allee effect for stable equilibrium.

    Changes from V4:
    1. Add Allee factor: λ_c → λ_c · (N / (N + N_crit))
    2. N_crit: Critical population threshold (~20-50)
    3. All other dynamics same as V4
    """

    def __init__(self, params: Dict[str, float]):
        """Initialize with V4 parameters + N_crit."""
        self.params = params
        self.validate_parameters()

    def validate_parameters(self):
        """Ensure parameters are physically reasonable."""
        assert 0.001 <= self.params['r'] <= 0.5, "Recharge rate out of bounds"
        assert 10 <= self.params['K'] <= 200, "Carrying capacity out of bounds"
        assert 0.0001 <= self.params['alpha'] <= 0.5, "Reality coupling out of bounds"
        assert 0.001 <= self.params['beta'] <= 0.1, "Maintenance cost out of bounds"
        assert 0.01 <= self.params['gamma'] <= 1.0, "Composition cost out of bounds"
        assert self.params['phi_0'] > self.params['omega'], \
            "phi_0 must exceed omega for positive phi equilibrium"
        assert self.params['N_crit'] > 0, "Allee threshold must be positive"

    def ode_system_v5a(
        self,
        state: np.ndarray,
        t: float,
        R_func: callable
    ) -> np.ndarray:
        """
        V5A dynamics with Allee effect.

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
        r = self.params['r']
        K = self.params['K']
        alpha = self.params['alpha']
        beta = self.params['beta']
        gamma = self.params['gamma']
        lambda_0 = self.params['lambda_0']
        mu_0 = self.params['mu_0']
        sigma = self.params['sigma']
        omega = self.params['omega']
        kappa = self.params['kappa']
        phi_0 = self.params.get('phi_0', 0.06)
        rho_threshold = self.params.get('rho_threshold', 5.0)
        N_crit = self.params.get('N_crit', 30.0)  # NEW: Allee threshold

        # Reality input
        R = R_func(t)

        # Energy gate (same as V4)
        energy_gate = 1.0 / (1.0 + np.exp(-kappa * (rho - rho_threshold)))

        # Resonance factor
        R_resonance = R * np.cos(theta_rel)

        # Base composition rate (same as V4)
        lambda_c_base = lambda_0 * energy_gate * phi**2

        # NEW: Allee factor (reduces birth rate at low N)
        allee_factor = N / (N + N_crit)

        # V5A composition rate with Allee effect
        lambda_c = lambda_c_base * allee_factor

        # Death rate (density-dependent, same as V4)
        death_rate = mu_0 * (1 + sigma * (N / K))

        # Derivatives
        dE_dt = gamma * R - alpha * lambda_c * E_total - beta * N * E_total
        dN_dt = (lambda_c - death_rate) * N
        dphi_dt = phi_0 * r * (1 - phi) - lambda_c * phi
        dtheta_dt = -omega

        return np.array([dE_dt, dN_dt, dphi_dt, dtheta_dt])

    def simulate(
        self,
        t_span: Tuple[float, float],
        initial_state: np.ndarray,
        R_func: callable,
        dt: float = 1.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate V5A model.

        Args:
            t_span: (t_start, t_end)
            initial_state: [E, N, phi, theta]
            R_func: Reality input function
            dt: Output timestep

        Returns:
            (t_array, trajectory)
        """
        t_start, t_end = t_span
        t_eval = np.arange(t_start, t_end + dt, dt)

        trajectory = odeint(
            self.ode_system_v5a,
            initial_state,
            t_eval,
            args=(R_func,)
        )

        return t_eval, trajectory


def run_extended_v5a(params: Dict, initial_state: np.ndarray,
                     t_max: float = 100000, dt: float = 10.0) -> Dict:
    """
    Run V5A for extended time to verify stable equilibrium.

    Args:
        params: V5A model parameters (includes N_crit)
        initial_state: Starting state [E, N, phi, theta]
        t_max: Maximum simulation time
        dt: Output timestep

    Returns:
        Dictionary with trajectory and equilibrium analysis
    """
    print(f"\n{'='*70}")
    print("V5A EXTENDED SIMULATION (t=100,000)")
    print(f"{'='*70}")
    print(f"\nParameters:")
    print(f"  N_crit (Allee threshold): {params['N_crit']:.1f}")
    print(f"  Initial N: {initial_state[1]:.1f}")

    # Reality input (constant)
    R_func = lambda t: 1.0

    # Initialize V5A model
    v5a = NRMDynamicalSystemV5A(params)

    # Time points
    t_span = (0, t_max)

    print(f"\nIntegrating to t={t_max:,.0f}...")
    t_array, trajectory = v5a.simulate(t_span, initial_state, R_func, dt=dt)

    # Extract variables
    E = trajectory[:, 0]
    N = trajectory[:, 1]
    phi = trajectory[:, 2]
    theta = trajectory[:, 3]

    # Compute derivatives at final point
    final_state = trajectory[-1]
    final_derivs = v5a.ode_system_v5a(final_state, t_array[-1], R_func)

    # Equilibrium analysis (final 10%)
    final_window = int(0.1 * len(t_array))
    final_mean_N = np.mean(N[-final_window:])
    final_std_N = np.std(N[-final_window:])
    final_drift_N = (N[-1] - N[-final_window]) / (t_array[-1] - t_array[-final_window])

    # Check equilibrium
    drift_threshold = 1e-6
    at_equilibrium = all(abs(final_derivs) < drift_threshold)

    print(f"\n{'='*70}")
    print("EQUILIBRIUM ANALYSIS")
    print(f"{'='*70}")
    print(f"\nFinal State (t={t_max:,.0f}):")
    print(f"  E = {final_state[0]:.4f}")
    print(f"  N = {final_state[1]:.4f}")
    print(f"  φ = {final_state[2]:.4f}")

    print(f"\nFinal Derivatives:")
    print(f"  dE/dt = {final_derivs[0]:.6e}")
    print(f"  dN/dt = {final_derivs[1]:.6e}")
    print(f"  dφ/dt = {final_derivs[2]:.6e}")

    print(f"\nFinal Window Statistics:")
    print(f"  Mean N: {final_mean_N:.4f} ± {final_std_N:.4f}")
    print(f"  Drift rate: {final_drift_N:.6e}")

    if at_equilibrium:
        print(f"\n✅ EQUILIBRIUM REACHED")
        print(f"   Stable N = {final_state[1]:.2f} (>> N_crit = {params['N_crit']:.1f})")
    else:
        print(f"\n⚠️ NOT AT EQUILIBRIUM")
        print(f"   Largest drift: {max(abs(final_derivs)):.6e}")

    if final_state[1] < 0:
        print(f"\n❌ WARNING: N went negative ({final_state[1]:.2f})")
        print(f"   Allee effect insufficient to prevent collapse")
    elif final_state[1] < params['N_crit']:
        print(f"\n⚠️ WARNING: N below Allee threshold")
        print(f"   N = {final_state[1]:.2f} < N_crit = {params['N_crit']:.1f}")
    else:
        print(f"\n✅ SUCCESS: N stable above Allee threshold")
        print(f"   N = {final_state[1]:.2f} > N_crit = {params['N_crit']:.1f}")

    return {
        't_array': t_array,
        'trajectory': trajectory,
        'final_state': final_state,
        'final_derivs': final_derivs,
        'at_equilibrium': at_equilibrium,
        'final_mean_N': final_mean_N,
        'final_std_N': final_std_N,
        'final_drift_N': final_drift_N
    }


def compare_v4_v5a(params_v4: Dict, params_v5a: Dict,
                   initial_state: np.ndarray, t_max: float = 50000) -> Dict:
    """
    Compare V4 (no Allee) vs V5A (with Allee) trajectories.

    Args:
        params_v4: V4 parameters (no N_crit)
        params_v5a: V5A parameters (with N_crit)
        initial_state: Starting state
        t_max: Simulation time

    Returns:
        Comparison results
    """
    print(f"\n{'='*70}")
    print("V4 vs V5A COMPARISON")
    print(f"{'='*70}")

    # Import V4 system
    from paper7_v4_energy_threshold import NRMDynamicalSystemV4

    # Reality input
    R_func = lambda t: 1.0

    # Run V4
    print("\nRunning V4 (no Allee effect)...")
    v4 = NRMDynamicalSystemV4(params_v4)
    t_v4 = np.arange(0, t_max + 10, 10)
    traj_v4 = odeint(v4.ode_system_v4, initial_state, t_v4, args=(R_func,))

    # Run V5A
    print("Running V5A (with Allee effect)...")
    v5a = NRMDynamicalSystemV5A(params_v5a)
    t_v5a, traj_v5a = v5a.simulate((0, t_max), initial_state, R_func, dt=10)

    print(f"\nV4 Final State (t={t_max:,.0f}):")
    print(f"  N = {traj_v4[-1, 1]:.2f}")
    print(f"  E = {traj_v4[-1, 0]:.2f}")

    print(f"\nV5A Final State (t={t_max:,.0f}):")
    print(f"  N = {traj_v5a[-1, 1]:.2f}")
    print(f"  E = {traj_v5a[-1, 0]:.2f}")

    # Check if V4 went negative
    v4_went_negative = np.any(traj_v4[:, 1] < 0)
    v5a_went_negative = np.any(traj_v5a[:, 1] < 0)

    print(f"\nStability Check:")
    print(f"  V4 went negative: {'YES ❌' if v4_went_negative else 'NO ✅'}")
    print(f"  V5A went negative: {'YES ❌' if v5a_went_negative else 'NO ✅'}")

    return {
        't_v4': t_v4,
        'traj_v4': traj_v4,
        't_v5a': t_v5a,
        'traj_v5a': traj_v5a,
        'v4_went_negative': v4_went_negative,
        'v5a_went_negative': v5a_went_negative
    }


def generate_figures(v5a_results: Dict, comparison: Dict, output_dir: Path):
    """
    Generate 6-panel publication figure.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    fig.suptitle("Paper 7: V5A with Allee Effect - Stable Equilibrium",
                fontsize=16, fontweight='bold')

    # Panel A: V5A population trajectory
    ax = fig.add_subplot(gs[0, 0])
    t = v5a_results['t_array']
    N = v5a_results['trajectory'][:, 1]
    ax.plot(t, N, 'b-', lw=2)
    ax.axhline(v5a_results['final_state'][1], color='r', linestyle='--',
               label=f'Final N = {v5a_results["final_state"][1]:.1f}', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('A) V5A Population (t=100,000)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel B: V4 vs V5A comparison
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(comparison['t_v4'], comparison['traj_v4'][:, 1], 'r-',
            label='V4 (no Allee)', lw=2, alpha=0.7)
    ax.plot(comparison['t_v5a'], comparison['traj_v5a'][:, 1], 'b-',
            label='V5A (with Allee)', lw=2, alpha=0.7)
    ax.axhline(0, color='k', linestyle=':', label='N=0 (impossible)', lw=1)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('B) V4 vs V5A Comparison', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel C: Energy dynamics
    ax = fig.add_subplot(gs[1, 0])
    E = v5a_results['trajectory'][:, 0]
    ax.plot(t, E, 'g-', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Energy E')
    ax.set_title('C) V5A Energy Dynamics', fontweight='bold')
    ax.grid(alpha=0.3)

    # Panel D: Resonance dynamics
    ax = fig.add_subplot(gs[1, 1])
    phi = v5a_results['trajectory'][:, 2]
    ax.plot(t, phi, 'purple', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Resonance φ')
    ax.set_title('D) V5A Resonance Dynamics', fontweight='bold')
    ax.grid(alpha=0.3)

    # Panel E: Final window (zoom)
    ax = fig.add_subplot(gs[2, 0])
    final_window = int(0.1 * len(t))
    t_final = t[-final_window:]
    N_final = N[-final_window:]
    ax.plot(t_final, N_final, 'b-', lw=2)
    ax.axhline(v5a_results['final_mean_N'], color='r', linestyle='--',
               label=f'Mean: {v5a_results["final_mean_N"]:.2f}', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('E) Final 10% Window (Equilibrium Check)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel F: Drift rates
    ax = fig.add_subplot(gs[2, 1])
    derivs_labels = ['dE/dt', 'dN/dt', 'dφ/dt']
    derivs_values = [v5a_results['final_derivs'][i] for i in range(3)]
    colors = ['green', 'blue', 'purple']

    bars = ax.bar(derivs_labels, np.abs(derivs_values), color=colors, alpha=0.7)
    ax.axhline(1e-6, color='k', linestyle='--', label='Equilibrium threshold', lw=2)
    ax.set_ylabel('|Derivative| (absolute value)')
    ax.set_yscale('log')
    ax.set_title('F) Final Drift Rates (Equilibrium)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3, axis='y')

    # Add values as text
    for bar, val in zip(bars, derivs_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height*1.5,
                f'{val:.2e}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()

    output_path = output_dir / f"paper7_v5a_allee_effect_{timestamp}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Figure saved: {output_path}")
    plt.close()


def main():
    """
    Main execution: Test V5A with Allee effect.
    """
    print("="*70)
    print("PAPER 7: V5A MODEL - ALLEE EFFECT FOR STABLE EQUILIBRIUM")
    print("="*70)
    print("\nGoal: Fix V4 instability by adding Allee effect")
    print("Hypothesis: Allee factor prevents collapse at low N")
    print("Test: Run to t=100,000 and verify stable equilibrium")

    # V4 base parameters
    params_v4 = {
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

    # V5A parameters: V4 + Allee threshold
    params_v5a = params_v4.copy()
    params_v5a['N_crit'] = 30.0  # Allee threshold

    # Initial state (low population to stress-test)
    initial_state = np.array([100.0, 10.0, 0.5, 0.0])  # [E, N, phi, theta]

    # Run V5A extended simulation
    v5a_results = run_extended_v5a(params_v5a, initial_state, t_max=100000, dt=10.0)

    # Compare V4 vs V5A
    comparison = compare_v4_v5a(params_v4, params_v5a, initial_state, t_max=50000)

    # Generate figures
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_figures(v5a_results, comparison, output_dir)

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = results_dir / f"paper7_v5a_allee_effect_{timestamp}.json"

    results_data = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'purpose': 'V5A with Allee effect for stable equilibrium',
            'params_v5a': params_v5a,
            'N_crit': params_v5a['N_crit']
        },
        'v5a_final_state': {
            'E': float(v5a_results['final_state'][0]),
            'N': float(v5a_results['final_state'][1]),
            'phi': float(v5a_results['final_state'][2]),
            'at_equilibrium': bool(v5a_results['at_equilibrium'])
        },
        'v5a_derivatives': {
            'dE_dt': float(v5a_results['final_derivs'][0]),
            'dN_dt': float(v5a_results['final_derivs'][1]),
            'dphi_dt': float(v5a_results['final_derivs'][2])
        },
        'comparison': {
            'v4_final_N': float(comparison['traj_v4'][-1, 1]),
            'v5a_final_N': float(comparison['traj_v5a'][-1, 1]),
            'v4_went_negative': bool(comparison['v4_went_negative']),
            'v5a_went_negative': bool(comparison['v5a_went_negative'])
        }
    }

    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)

    print(f"\n✅ Results saved: {results_path}")

    # Final verdict
    print(f"\n{'='*70}")
    print("FINAL VERDICT")
    print(f"{'='*70}")

    if v5a_results['at_equilibrium'] and v5a_results['final_state'][1] > params_v5a['N_crit']:
        print("\n✅ SUCCESS: V5A achieves stable equilibrium!")
        print(f"   N = {v5a_results['final_state'][1]:.2f} > N_crit = {params_v5a['N_crit']:.1f}")
        print(f"   Allee effect prevents collapse")
        print(f"   Ready for Phase 6 CLE (stochastic extension)")
    else:
        print("\n❌ FAILURE: V5A did not achieve stable equilibrium")
        print(f"   Need to adjust N_crit or add additional stabilizing mechanisms")

    print(f"\n{'='*70}")


if __name__ == '__main__':
    main()
