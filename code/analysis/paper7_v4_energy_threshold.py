#!/usr/bin/env python3
"""
Paper 7: V4 Model - Fixed Energy Threshold

Purpose: Fix V3's energy threshold issue to enable sustained dynamics

Root Cause from V3:
- V3 fixed phi dynamics (phi > 0) but still collapsed
- Energy gate: energy_gate = 1 / (1 + exp(-0.1*(rho - 40)))
- At N=1, E≈6: rho = 6 << 40 → energy_gate ≈ 0.03 (too low)
- lambda_c = lambda_0 * 0.03 * phi² ≈ 0.007 << lambda_d = 0.8
- Result: Insufficient composition to sustain population

V4 Fixes:
1. Lower energy threshold: rho_threshold = 40 → 5 (attainable at low N)
2. Increase recharge rate: r = 0.05 → 0.15 (faster energy buildup)
3. Keep phi_0 source term from V3 (positive phi equilibrium)

Expected Result:
- At N=1, E≈6: rho = 6 > 5 (threshold)
- energy_gate ≈ 0.73 (much higher!)
- lambda_c ≈ 0.29 > mu_0 = 0.8 (need further tuning)
- Population should sustain or grow

Date: 2025-10-27 (Cycle 380)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
from pathlib import Path
from scipy.integrate import odeint
from scipy.optimize import minimize, differential_evolution, root
from typing import Dict, List, Tuple, Any
import sys

sys.path.append(str(Path(__file__).parent.parent))


class NRMDynamicalSystemV4:
    """
    V4 model: Fixed energy threshold for sustained dynamics.

    Changes from V3:
    1. Lower energy threshold (rho_threshold = 5 instead of 40)
    2. Higher recharge rate (r = 0.15 instead of 0.05)
    3. Keep phi_0 source term from V3
    4. All dynamics in rotating frame
    """

    def __init__(self, params: Dict[str, float]):
        """Initialize with physically constrained parameters."""
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

    def ode_system_v4(
        self,
        state: np.ndarray,
        t: float,
        R_func: callable
    ) -> np.ndarray:
        """
        V4 dynamics with fixed energy threshold.

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
        rho_threshold = self.params.get('rho_threshold', 5.0)  # NEW: Lower threshold

        # Reality forcing
        R_t = R_func(t)

        # V4 IMPROVED: Composition rate with lower energy threshold
        energy_gate = 1.0 / (1.0 + np.exp(-0.1 * (rho - rho_threshold)))
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

        # V3 corrected phi dynamics (from previous fix)
        dphi_dt = phi_0 - omega * np.sin(theta_rel) - kappa * phi

        # Relative phase evolution (rotating frame)
        dtheta_rel_dt = 0.01 * (N - 50)

        return np.array([dE_dt, dN_dt, dphi_dt, dtheta_rel_dt])

    def simulate(
        self,
        t_span: np.ndarray,
        initial_state: np.ndarray,
        R_func: callable
    ) -> np.ndarray:
        """Integrate V4 ODE system."""
        solution = odeint(
            self.ode_system_v4,
            initial_state,
            t_span,
            args=(R_func,)
        )
        return solution


def test_v4_sustained_dynamics():
    """
    Test if V4 model achieves sustained dynamics.
    """
    print("\n" + "=" * 70)
    print("V4 MODEL SUSTAINED DYNAMICS TEST")
    print("=" * 70)
    print()

    # V4 parameters with energy threshold fix + balanced composition/decomposition
    params = {
        'r': 0.15,          # INCREASED: Faster energy recharge
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 2.5,    # INCREASED: Higher base composition rate (was 1.5)
        'mu_0': 0.4,        # DECREASED: Lower decomposition rate (was 0.6)
        'sigma': 0.1,
        'omega': 0.02,
        'kappa': 0.1,
        'phi_0': 0.06,      # From V3: ensures positive phi
        'rho_threshold': 5.0  # NEW: Lower energy threshold (was 40 in V2/V3)
    }

    model = NRMDynamicalSystemV4(params)
    print("✓ V4 model created")
    print()
    print("Key parameters:")
    print(f"  r (recharge):        {params['r']:.2f} (was 0.05)")
    print(f"  lambda_0 (composition): {params['lambda_0']:.2f} (was 1.0)")
    print(f"  mu_0 (decomposition):   {params['mu_0']:.2f} (was 0.8)")
    print(f"  rho_threshold:       {params['rho_threshold']:.1f} (was 40)")
    print(f"  phi_0 (source):      {params['phi_0']:.2f}")
    print()

    # Energy gate analysis
    print("Energy gate analysis:")
    print("  energy_gate = 1 / (1 + exp(-0.1*(rho - rho_threshold)))")
    print()

    for rho_test in [1, 3, 5, 7, 10, 20]:
        energy_gate = 1.0 / (1.0 + np.exp(-0.1 * (rho_test - params['rho_threshold'])))
        print(f"  rho = {rho_test:2d}: energy_gate = {energy_gate:.4f}")

    print()
    print("At rho=5 (threshold): energy_gate = 0.50 (activated!)")
    print("At rho=6: energy_gate = 0.52")
    print("At rho=10: energy_gate = 0.62")
    print()

    # Composition rate analysis
    print("Composition rate check:")
    rho_test = 6.0  # Expected for N=1, E≈6
    phi_test = 0.5
    energy_gate = 1.0 / (1.0 + np.exp(-0.1 * (rho_test - params['rho_threshold'])))
    lambda_c = params['lambda_0'] * energy_gate * phi_test ** 2
    lambda_d = params['mu_0']

    print(f"  At rho={rho_test}, phi={phi_test}:")
    print(f"    energy_gate = {energy_gate:.4f}")
    print(f"    lambda_c = {lambda_c:.4f}")
    print(f"    lambda_d = {lambda_d:.4f}")
    print(f"    lambda_c - lambda_d = {lambda_c - lambda_d:.4f}")

    if lambda_c > lambda_d:
        print("    ✓ lambda_c > lambda_d: Population should GROW")
    elif lambda_c < lambda_d:
        print("    ✗ lambda_c < lambda_d: Population will COLLAPSE")
        print("    Need higher lambda_0 or lower mu_0")
    else:
        print("    ⚠️ lambda_c ≈ lambda_d: Equilibrium")

    print()

    # Simulate
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

    # Assess result
    if final_state[1] > 5.0:
        print(f"  ✅ SUSTAINED: N={final_state[1]:.2f} > 5.0")
    elif final_state[1] <= 1.01:
        print(f"  ✗ COLLAPSED: N={final_state[1]:.2f} ≈ 1.0")
    else:
        print(f"  ⚠️ INTERMEDIATE: N={final_state[1]:.2f}")

    print()

    # Try equilibrium finding
    print("Attempting equilibrium finding:")

    def equilibrium_condition(state):
        return model.ode_system_v4(state, t=0, R_func=R_func)

    initial_guesses = [
        np.array([100.0, 50.0, 0.5, 0.0]),
        np.array([150.0, 50.0, 0.6, 0.5]),
        np.array([80.0, 50.0, 0.4, -0.5]),
    ]

    equilibrium_found = False
    for i, guess in enumerate(initial_guesses):
        result = root(equilibrium_condition, x0=guess, method='hybr')
        residual = np.abs(equilibrium_condition(result.x)) if result.success else np.array([np.inf]*4)
        max_residual = np.max(residual)
        converged = max_residual < 1e-6

        print(f"  Guess {i+1}: success={result.success}, converged={converged}, max_residual={max_residual:.2e}")
        if converged:
            print(f"    ✅ EQUILIBRIUM FOUND: E={result.x[0]:.2f}, N={result.x[1]:.2f}, "
                  f"phi={result.x[2]:.4f}, theta_rel={result.x[3]:.4f}")
            equilibrium_found = True

    print()
    print("=" * 70)

    return equilibrium_found, final_state


def main():
    """Execute V4 model testing."""
    equilibrium_found, final_state = test_v4_sustained_dynamics()

    print()
    print("=" * 70)
    print("V4 MODEL STATUS")
    print("=" * 70)

    if equilibrium_found and final_state[1] > 5.0:
        print("✅ SUCCESS:")
        print("  - Equilibrium found")
        print("  - Population sustained")
        print("  - Ready for bifurcation analysis")
        print()
        print("Next steps:")
        print("  - Run bifurcation analysis on V4")
        print("  - Generate regime diagrams")
        print("  - Compare to Paper 2 empirical boundaries")
    elif final_state[1] > 5.0:
        print("⚠️ PARTIAL SUCCESS:")
        print("  - Population sustained")
        print("  - But equilibrium not found (solver issue?)")
        print()
        print("Diagnosis needed:")
        print("  - Check equilibrium existence analytically")
        print("  - Try different initial guesses")
    else:
        print("✗ STILL COLLAPSING:")
        print("  - Energy threshold fix insufficient")
        print("  - Need higher lambda_0 or lower mu_0")
        print()
        print("Suggested parameter adjustments:")
        print("  - Increase lambda_0: 1.5 → 2.0")
        print("  - Decrease mu_0: 0.6 → 0.4")
        print("  - Or both")

    print("=" * 70)


if __name__ == "__main__":
    main()
