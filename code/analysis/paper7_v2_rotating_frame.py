#!/usr/bin/env python3
"""
Paper 7: V2 Model - Rotating Frame Transformation

Purpose: Transform V2 constrained model to co-rotating frame to enable equilibrium analysis

Motivation:
Original V2 model has unbounded phase variable (theta grows without limit), preventing
fixed-point equilibria. This is consistent with NRM "perpetual motion" principle but
incompatible with classical bifurcation analysis.

Solution:
Transform to frame rotating with external frequency omega. In this frame, relative phase
theta_rel = theta_int - omega*t becomes a bounded variable with stationary equilibria.

Transformation:
- Original state: [E_total, N, phi, theta_int]
- Rotating frame state: [E_total, N, phi, theta_rel]
- Where: theta_rel = theta_int - omega*t

New dynamics:
- dtheta_rel/dt = dtheta_int/dt - omega = [omega + 0.01*(N - 50)] - omega = 0.01*(N - 50)
- Now dtheta_rel/dt = 0 when N = 50 (equilibrium condition satisfied!)

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


class NRMDynamicalSystemV2RotatingFrame:
    """
    V2 model in rotating frame: enables equilibrium analysis.

    Key differences from original V2:
    1. State variable theta_rel (relative phase) instead of theta_int (absolute phase)
    2. dtheta_rel/dt = 0.01*(N - 50) instead of omega + 0.01*(N - 50)
    3. Equilibria now exist when N = 50
    4. All other dynamics identical to V2
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

    def ode_system_rotating_frame(
        self,
        state: np.ndarray,
        t: float,
        R_func: callable
    ) -> np.ndarray:
        """
        Rotating frame NRM equations.

        State: [E_total, N, phi, theta_rel]

        Differences from original V2:
        - theta_rel is bounded (not growing with time)
        - dtheta_rel/dt = 0.01*(N - 50) [instead of omega + 0.01*(N - 50)]
        - dphi/dt uses theta_rel directly (external phase absorbed into transformation)
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

        # Resonance evolution in rotating frame
        # In rotating frame, external phase is effectively zero (absorbed into transformation)
        # So: dphi/dt = omega * sin(0 - theta_rel) - kappa * phi
        #            = -omega * sin(theta_rel) - kappa * phi
        dphi_dt = -omega * np.sin(theta_rel) - kappa * phi

        # Relative phase evolution
        # Original: dtheta_int/dt = omega + 0.01*(N - 50)
        # Rotating: dtheta_rel/dt = dtheta_int/dt - omega = 0.01*(N - 50)
        dtheta_rel_dt = 0.01 * (N - 50)

        return np.array([dE_dt, dN_dt, dphi_dt, dtheta_rel_dt])

    def simulate(
        self,
        t_span: np.ndarray,
        initial_state: np.ndarray,
        R_func: callable
    ) -> np.ndarray:
        """Integrate rotating frame ODE system."""
        solution = odeint(
            self.ode_system_rotating_frame,
            initial_state,
            t_span,
            args=(R_func,)
        )
        return solution

    def to_original_frame(
        self,
        t: np.ndarray,
        state_rotating: np.ndarray
    ) -> np.ndarray:
        """
        Convert rotating frame solution back to original frame.

        Args:
            t: Time array
            state_rotating: Solution in rotating frame [E, N, phi, theta_rel]

        Returns:
            state_original: Solution in original frame [E, N, phi, theta_int]
        """
        omega = self.params['omega']

        # theta_int = theta_rel + omega*t
        theta_int = state_rotating[:, 3] + omega * t

        # Other variables unchanged
        state_original = state_rotating.copy()
        state_original[:, 3] = theta_int

        return state_original

    def from_original_frame(
        self,
        t: float,
        state_original: np.ndarray
    ) -> np.ndarray:
        """
        Convert original frame state to rotating frame.

        Args:
            t: Current time
            state_original: State in original frame [E, N, phi, theta_int]

        Returns:
            state_rotating: State in rotating frame [E, N, phi, theta_rel]
        """
        omega = self.params['omega']

        # theta_rel = theta_int - omega*t
        theta_rel = state_original[3] - omega * t

        # Other variables unchanged
        state_rotating = state_original.copy()
        state_rotating[3] = theta_rel

        return state_rotating


def compare_frames():
    """
    Demonstrate equivalence between original and rotating frame formulations.

    Test:
    1. Simulate original V2 model
    2. Transform initial condition to rotating frame
    3. Simulate rotating frame model
    4. Transform rotating frame solution back to original
    5. Verify solutions match
    """
    print("\n" + "=" * 70)
    print("ROTATING FRAME VALIDATION")
    print("=" * 70)
    print("Testing equivalence: Original V2 ↔ Rotating Frame")
    print()

    # Parameters
    params = {
        'r': 0.05,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 1.0,
        'mu_0': 0.8,
        'sigma': 0.1,
        'omega': 0.02,
        'kappa': 0.1
    }

    # Import original V2 model
    try:
        from paper7_v2_constrained_model import NRMDynamicalSystemV2
        model_original = NRMDynamicalSystemV2(params)
        print("✓ Original V2 model loaded")
    except ImportError:
        print("✗ Original V2 model not found, skipping validation")
        return

    # Create rotating frame model
    model_rotating = NRMDynamicalSystemV2RotatingFrame(params)
    print("✓ Rotating frame model created")
    print()

    # Initial condition (original frame)
    initial_state_original = np.array([100.0, 10.0, 0.5, 0.0])

    # Time span
    t_span = np.linspace(0, 100, 1001)
    R_func = lambda t: 1.0

    # Simulate original model
    print("Simulating original V2 model...")
    solution_original = model_original.simulate(t_span, initial_state_original, R_func)
    print(f"  Final state: E={solution_original[-1, 0]:.2f}, N={solution_original[-1, 1]:.2f}, "
          f"phi={solution_original[-1, 2]:.4f}, theta={solution_original[-1, 3]:.2f}")

    # Transform to rotating frame
    initial_state_rotating = model_rotating.from_original_frame(0, initial_state_original)
    print()
    print("Simulating rotating frame model...")
    solution_rotating_frame = model_rotating.simulate(t_span, initial_state_rotating, R_func)

    # Transform back to original frame
    solution_rotating_converted = model_rotating.to_original_frame(t_span, solution_rotating_frame)
    print(f"  Final state: E={solution_rotating_converted[-1, 0]:.2f}, N={solution_rotating_converted[-1, 1]:.2f}, "
          f"phi={solution_rotating_converted[-1, 2]:.4f}, theta={solution_rotating_converted[-1, 3]:.2f}")

    # Compute differences
    diff = np.abs(solution_original - solution_rotating_converted)
    max_diff = np.max(diff, axis=0)
    mean_diff = np.mean(diff, axis=0)

    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print("Maximum difference (Original vs Rotating→Original):")
    print(f"  E_total: {max_diff[0]:.2e}")
    print(f"  N:       {max_diff[1]:.2e}")
    print(f"  phi:     {max_diff[2]:.2e}")
    print(f"  theta:   {max_diff[3]:.2e}")
    print()
    print("Mean difference:")
    print(f"  E_total: {mean_diff[0]:.2e}")
    print(f"  N:       {mean_diff[1]:.2e}")
    print(f"  phi:     {mean_diff[2]:.2e}")
    print(f"  theta:   {mean_diff[3]:.2e}")
    print()

    # Success criterion: differences < 1e-3 (tolerance for numerical integration)
    tolerance = 1e-3
    if np.all(max_diff < tolerance):
        print("✅ VALIDATION SUCCESSFUL: Rotating frame is equivalent to original V2")
        print(f"   All differences < {tolerance:.0e}")
    else:
        print("⚠️  VALIDATION FAILED: Significant differences detected")
        print(f"   Some differences >= {tolerance:.0e}")

    print("=" * 70)


def main():
    """Execute rotating frame validation."""
    compare_frames()

    print()
    print("=" * 70)
    print("ROTATING FRAME MODEL READY")
    print("=" * 70)
    print("Next steps:")
    print("  - Run equilibrium finding on rotating frame model")
    print("  - Bifurcation analysis should now succeed (equilibria exist!)")
    print("  - Stability analysis via Jacobian eigenvalues")
    print("  - Generate bifurcation diagrams")
    print("=" * 70)


if __name__ == "__main__":
    main()
