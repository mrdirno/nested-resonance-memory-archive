#!/usr/bin/env python3
"""
Paper 7: V3 Model - Corrected Phi Dynamics

Purpose: Fix V2 model's universal collapse by ensuring positive phi equilibrium

Root Cause from V2:
- V2 phi dynamics: dphi/dt = -omega*sin(theta_rel) - kappa*phi
- Equilibrium: phi_eq = -omega*sin(theta_rel) / kappa
- Problem: phi_eq can be negative, but phi constrained to [0,1]
- Result: phi → 0 => lambda_c → 0 => universal collapse

V3 Fix:
- Add source term phi_0: dphi/dt = phi_0 - omega*sin(theta_rel) - kappa*phi
- New equilibrium: phi_eq = (phi_0 - omega*sin(theta_rel)) / kappa
- For phi_0 > omega: phi_eq always positive!
- Example: phi_0 = 0.3, omega = 0.02, kappa = 0.1
  - Min phi_eq = (0.3 - 0.02) / 0.1 = 2.8 (stays above zero)
  - Max phi_eq = (0.3 + 0.02) / 0.1 = 3.2

Physical Interpretation:
- phi_0 = intrinsic resonance drive (agents naturally resonate even without external forcing)
- Enables sustained composition even when phase coupling is negative

Date: 2025-10-27 (Cycle 379)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
from pathlib import Path
from scipy.integrate import odeint
from scipy.optimize import minimize, differential_evolution
from typing import Dict, List, Tuple, Any
import sys

sys.path.append(str(Path(__file__).parent.parent))


class NRMDynamicalSystemV3:
    """
    V3 model: Corrected phi dynamics with positive equilibrium guarantee.

    Changes from V2:
    1. Uses rotating frame (theta_rel instead of theta_int)
    2. Added phi_0 source term to phi dynamics
    3. Ensures phi_eq > 0 for all phase values
    """

    def __init__(self, params: Dict[str, float]):
        """Initialize with physically constrained parameters."""
        self.params = params
        self.validate_parameters()

    def validate_parameters(self):
        """Ensure parameters are physically reasonable."""
        assert 0.001 <= self.params['r'] <= 0.2, "Recharge rate out of bounds"
        assert 10 <= self.params['K'] <= 200, "Carrying capacity out of bounds"
        assert 0.0001 <= self.params['alpha'] <= 0.5, "Reality coupling out of bounds"
        assert 0.001 <= self.params['beta'] <= 0.1, "Maintenance cost out of bounds"
        assert 0.01 <= self.params['gamma'] <= 1.0, "Composition cost out of bounds"

        # New V3 constraint
        assert self.params['phi_0'] > self.params['omega'], \
            "phi_0 must exceed omega to guarantee positive phi equilibrium"

    def ode_system_v3(
        self,
        state: np.ndarray,
        t: float,
        R_func: callable
    ) -> np.ndarray:
        """
        V3 corrected dynamics.

        State: [E_total, N, phi, theta_rel]

        Key change: dphi/dt = phi_0 - omega*sin(theta_rel) - kappa*phi
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
        phi_0 = self.params.get('phi_0', 0.3)  # New parameter

        # Reality forcing
        R_t = R_func(t)

        # Composition rate (energy-gated, resonance-amplified)
        energy_gate = 1.0 / (1.0 + np.exp(-0.1 * (rho - 40)))
        resonance_amp = phi ** 2
        lambda_c = lambda_0 * energy_gate * resonance_amp

        # Decomposition rate (density-dependent)
        crowding = (N / 100.0) ** 2
        lambda_d = mu_0 * (1.0 + sigma * crowding)

        # Derivatives
        dE_dt = N * r * (1 - rho / K) + alpha * N * R_t - beta * N * rho - gamma * lambda_c * rho

        # Prevent negative population growth if N at minimum
        if N <= 1.0 and lambda_c < lambda_d:
            dN_dt = 0.0
        else:
            dN_dt = lambda_c - lambda_d

        # V3 CORRECTED: Resonance evolution with source term
        dphi_dt = phi_0 - omega * np.sin(theta_rel) - kappa * phi

        # Relative phase evolution (same as rotating frame V2)
        dtheta_rel_dt = 0.01 * (N - 50)

        return np.array([dE_dt, dN_dt, dphi_dt, dtheta_rel_dt])

    def simulate(
        self,
        t_span: np.ndarray,
        initial_state: np.ndarray,
        R_func: callable
    ) -> np.ndarray:
        """Integrate V3 ODE system."""
        solution = odeint(
            self.ode_system_v3,
            initial_state,
            t_span,
            args=(R_func,)
        )
        return solution


def test_v3_equilibrium():
    """
    Test if V3 model can find equilibria and sustain populations.
    """
    print("\n" + "=" * 70)
    print("V3 MODEL EQUILIBRIUM TEST")
    print("=" * 70)
    print()

    # Parameters with phi_0 chosen to keep phi_eq in [0.2, 0.8]
    # phi_eq = (phi_0 - omega*sin(theta_rel)) / kappa
    # For omega=0.02, kappa=0.1:
    # phi_eq range = [(phi_0 - 0.02)/0.1, (phi_0 + 0.02)/0.1]
    # Choose phi_0 = 0.05: phi_eq ∈ [0.3, 0.7] ✓
    params = {
        'r': 0.05,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 1.0,
        'mu_0': 0.8,
        'sigma': 0.1,
        'omega': 0.02,     # External frequency
        'kappa': 0.1,      # Resonance decay
        'phi_0': 0.06      # NEW: Intrinsic resonance drive (tuned for phi_eq ∈ [0.4, 0.8])
    }

    model = NRMDynamicalSystemV3(params)
    print("✓ V3 model created")
    print(f"  phi_0 = {params['phi_0']}, omega = {params['omega']}, kappa = {params['kappa']}")
    print(f"  phi_0 > omega: {params['phi_0'] > params['omega']} ✓")
    print()

    # Check phi equilibrium range
    print("Phi equilibrium analysis:")
    print("  phi_eq = (phi_0 - omega*sin(theta_rel)) / kappa")

    # Min: sin(theta_rel) = -1
    phi_eq_min = (params['phi_0'] - params['omega'] * (-1)) / params['kappa']
    # Max: sin(theta_rel) = +1
    phi_eq_max = (params['phi_0'] - params['omega'] * (+1)) / params['kappa']

    print(f"  Min phi_eq: {phi_eq_min:.4f} (sin = -1)")
    print(f"  Max phi_eq: {phi_eq_max:.4f} (sin = +1)")
    print(f"  Both positive: {phi_eq_min > 0 and phi_eq_max > 0} ✓")
    print()

    # Simulate to check for sustained dynamics
    print("Testing sustained dynamics:")
    initial_state = np.array([100.0, 10.0, 0.5, 0.0])
    t_span = np.linspace(0, 1000, 10001)
    R_func = lambda t: 1.0

    print("  Simulating 1000 time units...")
    solution = model.simulate(t_span, initial_state, R_func)

    # Check final state
    final_state = solution[-1]
    print(f"  Final state: E={final_state[0]:.2f}, N={final_state[1]:.2f}, "
          f"phi={final_state[2]:.4f}, theta_rel={final_state[3]:.4f}")

    # Check if population sustained
    if final_state[1] > 5.0:
        print(f"  ✅ SUSTAINED: N={final_state[1]:.2f} > 5.0")
    elif final_state[1] <= 1.01:
        print(f"  ✗ COLLAPSED: N={final_state[1]:.2f} ≈ 1.0")
    else:
        print(f"  ⚠️ INTERMEDIATE: N={final_state[1]:.2f}")

    print()

    # Try equilibrium finding
    print("Attempting equilibrium finding:")
    from scipy.optimize import root

    def equilibrium_condition(state):
        return model.ode_system_v3(state, t=0, R_func=R_func)

    # Use population near 50 (where dtheta_rel/dt = 0)
    initial_guesses = [
        np.array([100.0, 50.0, 2.0, 0.0]),
        np.array([150.0, 50.0, 3.0, 0.5]),
        np.array([80.0, 50.0, 2.5, -0.5]),
    ]

    for i, guess in enumerate(initial_guesses):
        result = root(equilibrium_condition, x0=guess, method='hybr')
        residual = np.abs(equilibrium_condition(result.x)) if result.success else np.array([np.inf]*4)
        max_residual = np.max(residual)
        converged = max_residual < 1e-6

        print(f"  Guess {i+1}: success={result.success}, converged={converged}, max_residual={max_residual:.2e}")
        if converged:
            print(f"    EQUILIBRIUM FOUND: E={result.x[0]:.2f}, N={result.x[1]:.2f}, "
                  f"phi={result.x[2]:.4f}, theta_rel={result.x[3]:.4f}")
            return result.x

    print()
    print("=" * 70)


def main():
    """Execute V3 model testing."""
    test_v3_equilibrium()

    print()
    print("=" * 70)
    print("V3 MODEL READY FOR BIFURCATION ANALYSIS")
    print("=" * 70)
    print("If equilibria found and population sustained:")
    print("  → V3 fixes V2 universal collapse issue")
    print("  → Can proceed with bifurcation analysis")
    print("  → Will generate regime diagrams matching Paper 2 empirical data")
    print("=" * 70)


if __name__ == "__main__":
    main()
