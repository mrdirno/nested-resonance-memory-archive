#!/usr/bin/env python3
"""
Paper 7: V5B Model - Energy Reservoir for Stable Equilibrium

Purpose: Fix V4 fundamental instability by decoupling energy input from consumption.

V4 Failure: Energy depletes (E: 2411 → 12) causing birth rate collapse
V5A Failure: Allee effect made it worse (reduced births when already marginal)

V5B Solution: Energy Reservoir with Buffer
- E_reservoir: Stores incoming energy from reality (γR)
- E_pop: Energy available to population (used for births)
- Transfer: r_transfer · (E_reservoir - E_pop)
- Buffer prevents rapid depletion cascade

System Equations:
    dE_r/dt = γR - r_transfer·(E_r - E_p)
    dE_p/dt = r_transfer·(E_r - E_p) - αλ_c·E_p - βN·E_p
    dN/dt = (λ_c - λ_d)·N
    dφ/dt = φ₀r(1-φ) - λ_c·φ
    dθ/dt = -ω

Where:
- E_r: Reservoir energy (input buffer)
- E_p: Population energy (available for consumption)
- r_transfer: Transfer rate (coupling strength)

Expected Result:
- Reservoir buffers energy fluctuations
- Prevents E_p → 0 cascade
- Stable equilibrium with N >> 1

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


class NRMDynamicalSystemV5B:
    """
    V5B model: V4 + Energy reservoir with buffering.

    Changes from V4:
    1. Split energy into E_reservoir and E_pop (5D system)
    2. Add transfer dynamics between reservoir and population
    3. r_transfer: transfer rate parameter
    """

    def __init__(self, params: Dict[str, float]):
        """Initialize with V4 parameters + r_transfer."""
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
        assert self.params['r_transfer'] > 0, "Transfer rate must be positive"

    def ode_system_v5b(
        self,
        state: np.ndarray,
        t: float,
        R_func: callable
    ) -> np.ndarray:
        """
        V5B dynamics with energy reservoir.

        State: [E_reservoir, E_pop, N, phi, theta_rel]
        (5D system)
        """
        E_reservoir, E_pop, N, phi, theta_rel = state

        # Enforce constraints
        N = max(1.0, N)
        E_reservoir = max(0.0, E_reservoir)
        E_pop = max(0.0, E_pop)
        phi = np.clip(phi, 0.0, 1.0)

        # Energy density (based on population energy)
        rho = E_pop / N

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
        r_transfer = self.params.get('r_transfer', 0.1)  # NEW: Transfer rate

        # Reality input
        R = R_func(t)

        # Energy gate (based on population energy)
        energy_gate = 1.0 / (1.0 + np.exp(-kappa * (rho - rho_threshold)))

        # Resonance factor
        R_resonance = R * np.cos(theta_rel)

        # Composition rate (same as V4)
        lambda_c = lambda_0 * energy_gate * phi**2

        # Death rate (density-dependent)
        death_rate = mu_0 * (1 + sigma * (N / K))

        # NEW: Energy transfer between reservoir and population
        energy_transfer = r_transfer * (E_reservoir - E_pop)

        # Derivatives
        dE_reservoir_dt = gamma * R - energy_transfer  # Input minus transfer out
        dE_pop_dt = energy_transfer - alpha * lambda_c * E_pop - beta * N * E_pop  # Transfer in minus consumption
        dN_dt = (lambda_c - death_rate) * N
        dphi_dt = phi_0 * r * (1 - phi) - lambda_c * phi
        dtheta_dt = -omega

        return np.array([dE_reservoir_dt, dE_pop_dt, dN_dt, dphi_dt, dtheta_dt])

    def simulate(
        self,
        t_span: Tuple[float, float],
        initial_state: np.ndarray,
        R_func: callable,
        dt: float = 1.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate V5B model.

        Args:
            t_span: (t_start, t_end)
            initial_state: [E_reservoir, E_pop, N, phi, theta]
            R_func: Reality input function
            dt: Output timestep

        Returns:
            (t_array, trajectory)
        """
        t_start, t_end = t_span
        t_eval = np.arange(t_start, t_end + dt, dt)

        trajectory = odeint(
            self.ode_system_v5b,
            initial_state,
            t_eval,
            args=(R_func,)
        )

        return t_eval, trajectory


def run_extended_v5b(params: Dict, initial_state: np.ndarray,
                     t_max: float = 100000, dt: float = 10.0) -> Dict:
    """
    Run V5B for extended time to verify stable equilibrium.

    Args:
        params: V5B model parameters (includes r_transfer)
        initial_state: Starting state [E_reservoir, E_pop, N, phi, theta]
        t_max: Maximum simulation time
        dt: Output timestep

    Returns:
        Dictionary with trajectory and equilibrium analysis
    """
    print(f"\n{'='*70}")
    print("V5B EXTENDED SIMULATION (t=100,000)")
    print(f"{'='*70}")
    print(f"\nParameters:")
    print(f"  r_transfer (energy buffer rate): {params['r_transfer']:.3f}")
    print(f"  Initial E_reservoir: {initial_state[0]:.1f}")
    print(f"  Initial E_pop: {initial_state[1]:.1f}")
    print(f"  Initial N: {initial_state[2]:.1f}")

    # Reality input (constant)
    R_func = lambda t: 1.0

    # Initialize V5B model
    v5b = NRMDynamicalSystemV5B(params)

    # Time points
    t_span = (0, t_max)

    print(f"\nIntegrating to t={t_max:,.0f}...")
    t_array, trajectory = v5b.simulate(t_span, initial_state, R_func, dt=dt)

    # Extract variables
    E_reservoir = trajectory[:, 0]
    E_pop = trajectory[:, 1]
    N = trajectory[:, 2]
    phi = trajectory[:, 3]
    theta = trajectory[:, 4]

    # Compute derivatives at final point
    final_state = trajectory[-1]
    final_derivs = v5b.ode_system_v5b(final_state, t_array[-1], R_func)

    # Equilibrium analysis (final 10%)
    final_window = int(0.1 * len(t_array))
    final_mean_N = np.mean(N[-final_window:])
    final_std_N = np.std(N[-final_window:])
    final_drift_N = (N[-1] - N[-final_window]) / (t_array[-1] - t_array[-final_window])

    # Check equilibrium
    drift_threshold = 1e-6
    at_equilibrium = all(abs(final_derivs[:4]) < drift_threshold)  # Skip dθ (constant rotation)

    print(f"\n{'='*70}")
    print("EQUILIBRIUM ANALYSIS")
    print(f"{'='*70}")
    print(f"\nFinal State (t={t_max:,.0f}):")
    print(f"  E_reservoir = {final_state[0]:.4f}")
    print(f"  E_pop = {final_state[1]:.4f}")
    print(f"  N = {final_state[2]:.4f}")
    print(f"  φ = {final_state[3]:.4f}")

    print(f"\nFinal Derivatives:")
    print(f"  dE_r/dt = {final_derivs[0]:.6e}")
    print(f"  dE_p/dt = {final_derivs[1]:.6e}")
    print(f"  dN/dt = {final_derivs[2]:.6e}")
    print(f"  dφ/dt = {final_derivs[3]:.6e}")

    print(f"\nFinal Window Statistics:")
    print(f"  Mean N: {final_mean_N:.4f} ± {final_std_N:.4f}")
    print(f"  Drift rate: {final_drift_N:.6e}")

    if at_equilibrium:
        print(f"\n✅ EQUILIBRIUM REACHED")
        print(f"   Stable N = {final_state[2]:.2f}")
        print(f"   Energy buffered: E_r={final_state[0]:.1f}, E_p={final_state[1]:.1f}")
    else:
        print(f"\n⚠️ NOT AT EQUILIBRIUM")
        print(f"   Largest drift: {max(abs(final_derivs[:4])):.6e}")

    if final_state[2] < 0:
        print(f"\n❌ WARNING: N went negative ({final_state[2]:.2f})")
        print(f"   Energy reservoir insufficient to prevent collapse")
    elif final_state[2] < 10:
        print(f"\n⚠️ WARNING: N very low ({final_state[2]:.2f})")
        print(f"   System near collapse")
    else:
        print(f"\n✅ SUCCESS: N stable at healthy level")
        print(f"   N = {final_state[2]:.2f} >> 1")

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


def generate_figures(v5b_results: Dict, output_dir: Path):
    """
    Generate 6-panel publication figure.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    fig.suptitle("Paper 7: V5B with Energy Reservoir - Stable Equilibrium",
                fontsize=16, fontweight='bold')

    t = v5b_results['t_array']
    traj = v5b_results['trajectory']

    # Panel A: Population trajectory
    ax = fig.add_subplot(gs[0, 0])
    N = traj[:, 2]
    ax.plot(t, N, 'b-', lw=2)
    ax.axhline(v5b_results['final_state'][2], color='r', linestyle='--',
               label=f'Final N = {v5b_results["final_state"][2]:.1f}', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('A) V5B Population (t=100,000)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel B: Energy dynamics (reservoir + population)
    ax = fig.add_subplot(gs[0, 1])
    E_reservoir = traj[:, 0]
    E_pop = traj[:, 1]
    ax.plot(t, E_reservoir, 'g-', label='E_reservoir', lw=2)
    ax.plot(t, E_pop, 'orange', label='E_pop', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Energy')
    ax.set_title('B) Energy Buffering (Reservoir + Population)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel C: Resonance dynamics
    ax = fig.add_subplot(gs[1, 0])
    phi = traj[:, 3]
    ax.plot(t, phi, 'purple', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Resonance φ')
    ax.set_title('C) V5B Resonance Dynamics', fontweight='bold')
    ax.grid(alpha=0.3)

    # Panel D: Energy transfer (E_reservoir - E_pop)
    ax = fig.add_subplot(gs[1, 1])
    energy_diff = E_reservoir - E_pop
    ax.plot(t, energy_diff, 'brown', lw=2)
    ax.axhline(0, color='k', linestyle=':', lw=1)
    ax.set_xlabel('Time')
    ax.set_ylabel('E_reservoir - E_pop')
    ax.set_title('D) Energy Buffer Gradient', fontweight='bold')
    ax.grid(alpha=0.3)

    # Panel E: Final window (equilibrium check)
    ax = fig.add_subplot(gs[2, 0])
    final_window = int(0.1 * len(t))
    t_final = t[-final_window:]
    N_final = N[-final_window:]
    ax.plot(t_final, N_final, 'b-', lw=2)
    ax.axhline(v5b_results['final_mean_N'], color='r', linestyle='--',
               label=f'Mean: {v5b_results["final_mean_N"]:.2f}', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('E) Final 10% Window (Equilibrium Check)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel F: Drift rates
    ax = fig.add_subplot(gs[2, 1])
    derivs_labels = ['dE_r/dt', 'dE_p/dt', 'dN/dt', 'dφ/dt']
    derivs_values = [v5b_results['final_derivs'][i] for i in range(4)]
    colors = ['green', 'orange', 'blue', 'purple']

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
                f'{val:.2e}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()

    output_path = output_dir / f"paper7_v5b_energy_reservoir_{timestamp}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Figure saved: {output_path}")
    plt.close()


def main():
    """
    Main execution: Test V5B with energy reservoir.
    """
    print("="*70)
    print("PAPER 7: V5B MODEL - ENERGY RESERVOIR FOR STABLE EQUILIBRIUM")
    print("="*70)
    print("\nGoal: Fix V4 instability by buffering energy")
    print("Hypothesis: Reservoir prevents rapid energy depletion cascade")
    print("Test: Run to t=100,000 and verify stable equilibrium")

    # V4 base parameters
    params_v5b = {
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
        'rho_threshold': 5.0,
        'r_transfer': 0.1  # NEW: Energy transfer rate
    }

    # Initial state: [E_reservoir, E_pop, N, phi, theta]
    # Start with equal reservoir and population energy
    initial_state = np.array([100.0, 100.0, 10.0, 0.5, 0.0])

    # Run V5B extended simulation
    v5b_results = run_extended_v5b(params_v5b, initial_state, t_max=100000, dt=10.0)

    # Generate figures
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_figures(v5b_results, output_dir)

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = results_dir / f"paper7_v5b_energy_reservoir_{timestamp}.json"

    results_data = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'purpose': 'V5B with energy reservoir for stable equilibrium',
            'params_v5b': params_v5b,
            'r_transfer': params_v5b['r_transfer']
        },
        'v5b_final_state': {
            'E_reservoir': float(v5b_results['final_state'][0]),
            'E_pop': float(v5b_results['final_state'][1]),
            'N': float(v5b_results['final_state'][2]),
            'phi': float(v5b_results['final_state'][3]),
            'at_equilibrium': bool(v5b_results['at_equilibrium'])
        },
        'v5b_derivatives': {
            'dE_r_dt': float(v5b_results['final_derivs'][0]),
            'dE_p_dt': float(v5b_results['final_derivs'][1]),
            'dN_dt': float(v5b_results['final_derivs'][2]),
            'dphi_dt': float(v5b_results['final_derivs'][3])
        },
        'equilibrium_analysis': {
            'final_mean_N': float(v5b_results['final_mean_N']),
            'final_std_N': float(v5b_results['final_std_N']),
            'final_drift_N': float(v5b_results['final_drift_N'])
        }
    }

    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)

    print(f"\n✅ Results saved: {results_path}")

    # Final verdict
    print(f"\n{'='*70}")
    print("FINAL VERDICT")
    print(f"{'='*70}")

    if v5b_results['at_equilibrium'] and v5b_results['final_state'][2] > 10:
        print("\n✅ SUCCESS: V5B achieves stable equilibrium!")
        print(f"   N = {v5b_results['final_state'][2]:.2f} >> 1")
        print(f"   Energy reservoir prevents collapse")
        print(f"   Ready for Phase 6 CLE (stochastic extension)")
    else:
        print("\n❌ FAILURE: V5B did not achieve stable equilibrium")
        print(f"   Final N = {v5b_results['final_state'][2]:.2f}")
        if v5b_results['final_state'][2] < 0:
            print(f"   Population went negative - reservoir insufficient")
        print(f"   Need to adjust r_transfer or try hard floor approach")

    print(f"\n{'='*70}")


if __name__ == '__main__':
    main()
