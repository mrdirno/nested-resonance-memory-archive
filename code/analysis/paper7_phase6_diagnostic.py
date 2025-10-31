#!/usr/bin/env python3
"""
PAPER 7 PHASE 6: DIAGNOSTIC VERSION

Purpose: Add detailed logging to understand extinction mechanism

Date: 2025-10-31 (Cycle 788)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
"""

import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


def diagnostic_single_run():
    """Run single trajectory with detailed logging."""

    # V4 parameters
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

    # Initial state from Phase 5 steady state
    E = 2411.77
    N = 215.0
    phi = 0.6074
    theta_rel = 0.0

    dt = 0.1
    R = 1.0

    print("=" * 70)
    print("DIAGNOSTIC RUN: SINGLE TRAJECTORY WITH DETAILED LOGGING")
    print("=" * 70)
    print()
    print(f"Initial state: E={E:.2f}, N={N:.2f}, phi={phi:.4f}")
    print()
    print(f"{'Step':>6} {'Time':>8} {'E':>10} {'N':>10} {'phi':>8} {'rho':>8} {'λ_c':>8} {'λ_d':>8} {'dE/dt':>10} {'ΔN':>6}")
    print("-" * 110)

    np.random.seed(42)

    for step in range(100):  # First 10 seconds (100 steps at dt=0.1)
        t = step * dt

        # Compute current state
        rho = E / N if N > 0 else 0.0
        energy_gate = 1.0 / (1.0 + np.exp(-params['kappa'] * (rho - params['rho_threshold'])))
        lambda_c = params['lambda_0'] * energy_gate * phi**2
        crowding = (N / params['K'])**2
        lambda_d = params['mu_0'] * (1.0 + params['sigma'] * crowding)

        # Energy dynamics
        dE_dt = params['gamma'] * R - params['alpha'] * lambda_c * E - params['beta'] * N * E

        # Population dynamics (stochastic)
        if N > 0:
            birth_rate_total = lambda_c * N
            death_rate_total = lambda_d * N
            n_births = np.random.poisson(birth_rate_total * dt)
            n_deaths = np.random.poisson(death_rate_total * dt)
            delta_N = n_births - n_deaths
        else:
            delta_N = 0
            n_births = 0
            n_deaths = 0

        # Log every 10 steps
        if step % 10 == 0:
            print(f"{step:6d} {t:8.1f} {E:10.2f} {N:10.2f} {phi:8.4f} {rho:8.2f} {lambda_c:8.4f} {lambda_d:8.4f} {dE_dt:10.2f} {delta_N:6d}")

        # Update state
        E_new = E + dt * dE_dt
        E_new = max(E_new, 0.0)

        dphi_dt = params['phi_0'] * params['r'] * (1 - phi) - lambda_c * phi
        phi_new = phi + dt * dphi_dt
        phi_new = np.clip(phi_new, 0.0, 1.0)

        N_new = max(N + delta_N, 0)

        # Check for extinction
        if N_new == 0 and N > 0:
            print()
            print(f"⚠️ EXTINCTION at step {step}, t={t:.1f}")
            print(f"   Last state: E={E:.2f}, N={N:.0f}, phi={phi:.4f}, rho={rho:.2f}")
            print(f"   Rates: λ_c={lambda_c:.4f}, λ_d={lambda_d:.4f}")
            print(f"   Events: births={n_births}, deaths={n_deaths}, ΔN={delta_N}")
            break

        E, N, phi = E_new, N_new, phi_new

    print()
    print(f"Final state after {step} steps: E={E:.2f}, N={N:.2f}, phi={phi:.4f}")
    print()


if __name__ == "__main__":
    diagnostic_single_run()
