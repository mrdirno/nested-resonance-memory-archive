#!/usr/bin/env python3
"""
PAPER 7 PHASE 6: STOCHASTIC DEMOGRAPHIC V4 MODEL (V4 - SCALED R)

Purpose: Fix energy crash via resource input scaling

Based on diagnostic analysis:
- V1/V2/V3 had catastrophic energy loss (dE/dt = -10,515)
- Root cause: beta*N*E >> gamma*R (maintenance >> input)
- V3 tested reducing beta (failed)
- V4 tests increasing R to balance energy budget

Energy budget at steady state (dE/dt ≈ 0):
  gamma * R ≈ alpha * lambda_c * E + beta * N * E

From diagnostic (E=2411, N=215, lambda_c=0.60):
  Required R ≈ (0.1 * 0.60 * 2411 + 0.02 * 215 * 2411) / 0.3
            ≈ (144.8 + 10,371) / 0.3
            ≈ 35,053

Test: Increase R from 1.0 to 35,000 to balance maintenance cost

Date: 2025-10-31 (Cycle 789)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Callable
import sys

sys.path.append(str(Path(__file__).parent))


class StochasticDemographicV4ScaledR:
    """Stochastic V4 with scaled R to prevent energy crash."""

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

        # Energy dynamics (with SCALED R)
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

        return trajectory


def run_stochastic_ensemble_scaled_R(
    params: Dict,
    initial_state: np.ndarray,
    n_runs: int = 20,
    t_total: float = 5000.0,
    dt: float = 0.1,
    R_value: float = 35000.0
) -> Dict:
    """Run ensemble of stochastic simulations (SCALED R)."""
    print(f"\nRunning stochastic ensemble (SCALED R={R_value:.1f}, n={n_runs}, t={t_total})...")

    t_span = np.arange(0, t_total + dt, dt)
    R_func = lambda t: R_value

    all_trajectories = []

    for run_idx in range(n_runs):
        if (run_idx + 1) % 5 == 0:
            print(f"  Run {run_idx+1}/{n_runs}")

        model = StochasticDemographicV4ScaledR(params, dt=dt, random_seed=run_idx)
        trajectory = model.simulate(t_span, initial_state, R_func)
        all_trajectories.append(trajectory)

    all_trajectories = np.array(all_trajectories)

    # Calculate statistics (exclude transient: t > 500)
    transient_idx = int(500.0 / dt)
    N_steady = all_trajectories[:, transient_idx:, 1]

    mean_N_ensemble = []
    std_N_ensemble = []

    for run_idx in range(n_runs):
        N_run = N_steady[run_idx]
        mean_N_ensemble.append(np.mean(N_run))
        std_N_ensemble.append(np.std(N_run))

    mean_N_ensemble = np.array(mean_N_ensemble)
    std_N_ensemble = np.array(std_N_ensemble)

    overall_mean = np.mean(mean_N_ensemble)
    overall_std = np.std(N_steady.flatten())
    overall_cv = overall_std / overall_mean if overall_mean > 0 else 0.0

    within_run_cv = []
    for run_idx in range(n_runs):
        N_run = N_steady[run_idx]
        mean_run = np.mean(N_run)
        std_run = np.std(N_run)
        cv_run = std_run / mean_run if mean_run > 0 else 0.0
        within_run_cv.append(cv_run)

    within_run_cv = np.array(within_run_cv)
    mean_within_cv = np.mean(within_run_cv)

    print(f"\n  Overall mean N: {overall_mean:.2f}")
    print(f"  Overall std N: {overall_std:.2f}")
    print(f"  Overall CV: {overall_cv:.3f} ({overall_cv*100:.1f}%)")
    print(f"  Within-run CV (average): {mean_within_cv:.3f} ({mean_within_cv*100:.1f}%)")

    # Check for extinction
    extinction_count = 0
    for run_idx in range(n_runs):
        if all_trajectories[run_idx, -1, 1] == 0:
            extinction_count += 1

    print(f"  Extinction events: {extinction_count}/{n_runs} ({extinction_count/n_runs*100:.1f}%)")

    return {
        'trajectories': all_trajectories,
        't_span': t_span,
        'overall_mean': overall_mean,
        'overall_std': overall_std,
        'overall_cv': overall_cv,
        'mean_within_cv': mean_within_cv,
        'within_run_cv': within_run_cv,
        'mean_N_ensemble': mean_N_ensemble,
        'std_N_ensemble': std_N_ensemble,
        'extinction_count': extinction_count
    }


def diagnostic_single_run_scaled_R(R_value: float = 35000.0):
    """Run single trajectory with detailed logging (SCALED R)."""

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
    R = R_value

    print("=" * 70)
    print(f"DIAGNOSTIC RUN: SCALED R = {R_value:.1f}")
    print("=" * 70)
    print()
    print(f"Initial state: E={E:.2f}, N={N:.2f}, phi={phi:.4f}")
    print()
    print(f"{'Step':>6} {'Time':>8} {'E':>10} {'N':>10} {'phi':>8} {'rho':>8} {'λ_c':>8} {'λ_d':>8} {'dE/dt':>10} {'ΔN':>6}")
    print("-" * 110)

    np.random.seed(42)

    for step in range(100):  # First 10 seconds
        t = step * dt

        # Compute current state
        rho = E / N if N > 0 else 0.0
        energy_gate = 1.0 / (1.0 + np.exp(-params['kappa'] * (rho - params['rho_threshold'])))
        lambda_c = params['lambda_0'] * energy_gate * phi**2
        crowding = (N / params['K'])**2
        lambda_d = params['mu_0'] * (1.0 + params['sigma'] * crowding)

        # Energy dynamics (WITH SCALED R)
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


def main():
    """Main execution: stochastic V4 with scaled R."""
    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 6: STOCHASTIC V4 (V4 - SCALED R)")
    print("=" * 70)
    print()

    print("Fix: Increase R from 1.0 → 35,000 to balance energy budget")
    print("Goal: Prevent energy crash while maintaining population dynamics")
    print()

    # Original parameters (V4 sustained)
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

    empirical_cv = 0.092

    # Diagnostic run first
    print("\n" + "=" * 70)
    print("DIAGNOSTIC: First 10 seconds with R=35,000")
    print("=" * 70)
    diagnostic_single_run_scaled_R(R_value=35000.0)

    # Full ensemble test
    print("\n" + "=" * 70)
    print("TEST: Deterministic Steady State with Scaled R")
    print("=" * 70)
    initial_state = np.array([2411.77, 215.0, 0.6074, 0.0])

    results = run_stochastic_ensemble_scaled_R(
        params,
        initial_state,
        n_runs=20,
        t_total=5000.0,
        dt=0.1,
        R_value=35000.0
    )

    # Summary
    print("\n" + "=" * 70)
    print("STOCHASTIC V4 SUMMARY (SCALED R)")
    print("=" * 70)
    print()

    print(f"Paper 2 empirical CV: {empirical_cv:.3f} ({empirical_cv*100:.1f}%)")
    print(f"\nStochastic V4 (R=35,000) results:")
    print(f"  Overall CV (pooled): {results['overall_cv']:.3f} ({results['overall_cv']*100:.1f}%)")
    print(f"  Within-run CV (average): {results['mean_within_cv']:.3f} ({results['mean_within_cv']*100:.1f}%)")
    print(f"  Extinction rate: {results['extinction_count']}/{20} ({results['extinction_count']/20*100:.1f}%)")
    print()

    cv_error_within = abs(results['mean_within_cv'] - empirical_cv)

    if results['extinction_count'] > 0:
        print("⚠️ PARTIAL EXTINCTION")
        print(f"   {results['extinction_count']}/20 runs went extinct")
        print("   Hypothesis: R scaling insufficient OR initial conditions wrong")
    elif cv_error_within < 0.02:
        print("✅ HYPOTHESIS VALIDATED")
        print("   Scaled R prevents extinction, CV matches empirical!")
        print(f"   Error: {cv_error_within:.4f} (< 0.02 threshold)")
    elif cv_error_within < 0.05:
        print("⚠️ HYPOTHESIS PARTIALLY SUPPORTED")
        print("   Scaled R prevents extinction, but CV doesn't match exactly")
        print(f"   Error: {cv_error_within:.4f} (< 0.05)")
    else:
        print("❌ HYPOTHESIS REJECTED")
        print("   Scaled R prevents extinction but CV far from empirical")
        print(f"   Error: {cv_error_within:.4f} (> 0.05)")

    print()


if __name__ == "__main__":
    main()
