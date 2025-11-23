#!/usr/bin/env python3
"""
PAPER 7 PHASE 6: R VALUE SWEEP

Purpose: Find viable R range empirically

Findings from previous tests:
- R=1.0: Immediate energy crash (dE/dt=-10,515), extinction
- R=35,000: Energy explosion (E → 17,395), still extinction

Hypothesis: There might be a viable R range where system persists

Test: Sweep R from 1 to 35,000 to find persistence region

Date: 2025-10-31 (Cycle 789)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
from typing import Dict, Tuple, Callable
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


class StochasticDemographicV4:
    """Stochastic V4 for R sweep."""

    def __init__(self, params: Dict, dt: float = 0.1, random_seed: int = None):
        self.params = params
        self.dt = dt
        if random_seed is not None:
            np.random.seed(random_seed)

    def compute_rates(self, state: np.ndarray, R: float) -> Tuple[float, float]:
        """Compute birth and death rates from current state."""
        E, N, phi, theta_rel = state

        lambda_0 = self.params['lambda_0']
        mu_0 = self.params['mu_0']
        sigma = self.params['sigma']
        kappa = self.params['kappa']
        rho_threshold = self.params['rho_threshold']
        K = self.params['K']

        if N <= 0:
            return 0.0, 0.0

        rho = E / N
        energy_gate = 1.0 / (1.0 + np.exp(-kappa * (rho - rho_threshold)))
        lambda_c = lambda_0 * energy_gate * phi**2
        crowding = (N / K)**2
        lambda_d = mu_0 * (1.0 + sigma * crowding)

        return lambda_c, lambda_d

    def synchronized_step(self, state: np.ndarray, R: float) -> np.ndarray:
        """Synchronized update of all state variables."""
        E, N, phi, theta_rel = state

        r = self.params['r']
        alpha = self.params['alpha']
        beta = self.params['beta']
        gamma = self.params['gamma']
        phi_0 = self.params['phi_0']
        omega = self.params['omega']

        lambda_c, lambda_d = self.compute_rates(state, R)

        # Energy dynamics
        dE_dt = gamma * R - alpha * lambda_c * E - beta * N * E
        E_new = E + self.dt * dE_dt
        E_new = max(E_new, 0.0)

        # Phi dynamics
        dphi_dt = phi_0 * r * (1 - phi) - lambda_c * phi
        phi_new = phi + self.dt * dphi_dt
        phi_new = np.clip(phi_new, 0.0, 1.0)

        # Theta dynamics
        theta_rel_new = theta_rel - omega * self.dt

        # Population dynamics (stochastic)
        if N > 0:
            birth_rate_total = lambda_c * N
            death_rate_total = lambda_d * N
            n_births = np.random.poisson(birth_rate_total * self.dt)
            n_deaths = np.random.poisson(death_rate_total * self.dt)
            N_new = max(N + n_births - n_deaths, 0)
        else:
            N_new = 0

        return np.array([E_new, N_new, phi_new, theta_rel_new])

    def simulate(
        self,
        t_span: np.ndarray,
        initial_state: np.ndarray,
        R_func: Callable[[float], float]
    ) -> np.ndarray:
        """Simulate stochastic model."""
        n_steps = len(t_span)
        trajectory = np.zeros((n_steps, 4))
        trajectory[0] = initial_state

        state = initial_state.copy()

        for i in range(1, n_steps):
            t = t_span[i]
            R = R_func(t)
            state = self.synchronized_step(state, R)
            trajectory[i] = state

            # Early stopping if extinct
            if state[1] == 0:
                trajectory[i:] = state
                break

        return trajectory


def test_R_value(params: Dict, initial_state: np.ndarray, R_value: float, n_runs: int = 5, t_total: float = 1000.0, dt: float = 0.1) -> Dict:
    """Test single R value with small ensemble."""
    t_span = np.arange(0, t_total + dt, dt)
    R_func = lambda t: R_value

    extinction_count = 0
    mean_N_values = []

    for run_idx in range(n_runs):
        model = StochasticDemographicV4(params, dt=dt, random_seed=run_idx)
        trajectory = model.simulate(t_span, initial_state, R_func)

        # Check extinction
        if trajectory[-1, 1] == 0:
            extinction_count += 1

        # Mean N in latter half
        mid_idx = len(trajectory) // 2
        mean_N = np.mean(trajectory[mid_idx:, 1])
        mean_N_values.append(mean_N)

    mean_N_avg = np.mean(mean_N_values)

    return {
        'R': R_value,
        'extinction_count': extinction_count,
        'n_runs': n_runs,
        'mean_N': mean_N_avg,
        'extinction_rate': extinction_count / n_runs
    }


def main():
    """Main execution: R sweep."""
    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 6: R VALUE SWEEP")
    print("=" * 70)
    print()

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

    initial_state = np.array([2411.77, 215.0, 0.6074, 0.0])

    # Test R values (log scale)
    R_values = [1.0, 10.0, 100.0, 500.0, 1000.0, 5000.0, 10000.0, 20000.0, 35000.0]

    print("Testing R values (5 runs each, t=1000):")
    print()
    print(f"{'R':>10} {'Extinction':>12} {'Mean N':>10} {'Status':>20}")
    print("-" * 70)

    results = []
    for R_value in R_values:
        result = test_R_value(params, initial_state, R_value, n_runs=5, t_total=1000.0)
        results.append(result)

        status = "EXTINCT" if result['extinction_rate'] == 1.0 else f"PERSIST ({result['extinction_rate']*100:.0f}% extinct)"

        print(f"{R_value:10.1f} {result['extinction_count']}/5 ({result['extinction_rate']*100:3.0f}%) {result['mean_N']:10.2f} {status:>20}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    # Find viable R range (if any)
    viable_R = [r['R'] for r in results if r['extinction_rate'] < 1.0 and r['mean_N'] > 10]

    if viable_R:
        print(f"✅ Viable R range found: {min(viable_R):.1f} - {max(viable_R):.1f}")
        print(f"   These R values allow persistence with N > 10")
    else:
        print("❌ No viable R range found")
        print("   All tested R values lead to extinction")
        print()
        print("IMPLICATION:")
        print("   Problem is NOT just R scaling")
        print("   Likely causes:")
        print("   1. Deterministic steady state ≠ stochastic steady state")
        print("   2. Fundamental parameter mismatch (beta, alpha, etc.)")
        print("   3. Stochastic demographic noise incompatible with V4 params")

    print()


if __name__ == "__main__":
    main()
