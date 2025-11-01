#!/usr/bin/env python3
"""
PAPER 7 PHASE 6: INITIAL CONDITION SEARCH

Purpose: Find stochastic equilibrium empirically

Findings:
- V1-V3: All failed (universal extinction)
- V4: R scaling doesn't help (R=1 to R=35,000 all → extinction)
- Conclusion: Deterministic steady state ≠ stochastic steady state

Hypothesis: System CAN persist, but requires different initial conditions

Test: Sweep (N, E) space to find persistence region

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
    """Stochastic V4 for initial condition search."""

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


def test_initial_condition(params: Dict, N_init: float, E_init: float, R_value: float, n_runs: int = 3, t_total: float = 1000.0, dt: float = 0.1) -> Dict:
    """Test single initial condition."""
    initial_state = np.array([E_init, N_init, 0.6, 0.0])  # Use phi=0.6 as moderate value
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
        'N_init': N_init,
        'E_init': E_init,
        'extinction_count': extinction_count,
        'n_runs': n_runs,
        'mean_N': mean_N_avg,
        'extinction_rate': extinction_count / n_runs
    }


def main():
    """Main execution: initial condition search."""
    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 6: INITIAL CONDITION SEARCH")
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

    # Test grid of (N, E) values with R=1.0
    N_values = [10, 20, 50, 100, 150, 200, 215]  # Include deterministic N=215
    E_values = [50, 100, 200, 500, 1000, 2000, 2412]  # Include deterministic E=2412

    print("Testing (N, E) grid with R=1.0 (3 runs each, t=1000):")
    print()
    print(f"{'N':>6} {'E':>8} {'rho':>8} {'Ext.':>8} {'Mean N':>10} {'Status':>15}")
    print("-" * 70)

    results = []
    for N_init in N_values:
        for E_init in E_values:
            rho = E_init / N_init
            result = test_initial_condition(params, N_init, E_init, R_value=1.0, n_runs=3, t_total=1000.0)
            results.append(result)

            status = "EXTINCT" if result['extinction_rate'] == 1.0 else f"PERSIST"

            # Only print every few to save space
            if N_init in [10, 50, 100, 215] or (N_init == 20 and E_init in [50, 100, 200]):
                print(f"{N_init:6.0f} {E_init:8.0f} {rho:8.2f} {result['extinction_count']}/3 ({result['extinction_rate']*100:3.0f}%) {result['mean_N']:10.2f} {status:>15}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    # Find viable (N, E) combinations
    viable_conditions = [(r['N_init'], r['E_init']) for r in results if r['extinction_rate'] < 1.0 and r['mean_N'] > 5]

    if viable_conditions:
        print(f"✅ Found {len(viable_conditions)} viable initial conditions:")
        for N, E in viable_conditions[:10]:  # Show first 10
            print(f"   N={N:.0f}, E={E:.0f}, rho={E/N:.2f}")
        if len(viable_conditions) > 10:
            print(f"   ... and {len(viable_conditions)-10} more")
    else:
        print("❌ No viable initial conditions found")
        print()
        print("CRITICAL FINDING:")
        print("   Stochastic V4 model CANNOT persist with ANY tested parameters")
        print()
        print("ROOT CAUSE ANALYSIS:")
        print("   1. ✅ Tested R scaling (1 to 35,000) → all failed")
        print("   2. ✅ Tested initial conditions → all failed")
        print("   3. ⏳ Remaining: V4 parameters fundamentally incompatible")
        print()
        print("NEXT STEPS:")
        print("   1. Compare deterministic Phase 5 behavior")
        print("   2. Check for equation implementation errors")
        print("   3. Consider V4 → stochastic conversion requires parameter re-calibration")

    print()


if __name__ == "__main__":
    main()
