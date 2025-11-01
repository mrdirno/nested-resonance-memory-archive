#!/usr/bin/env python3
"""
PAPER 7 PHASE 6: STOCHASTIC DEMOGRAPHIC V4 MODEL (V5 - FIXED EQUATION)

Purpose: Fix fundamental equation error discovered via Phase 5 comparison

ROOT CAUSE IDENTIFIED:
- V1-V4 used WRONG energy equation:
  dE_dt = gamma*R - alpha*lambda_c*E - beta*N*E

- Phase 5 deterministic V4 uses CORRECT equation:
  dE_dt = N*r*(1 - rho/K) + alpha*N*R - beta*N*rho - gamma*lambda_c*rho

CRITICAL DIFFERENCE:
- V1-V4 missing N*r*(1-rho/K) term (intrinsic energy generation!)
- This explains universal extinction across all parameter combinations

V5 FIX:
- Use exact energy equation from deterministic Phase 5 V4
- Should enable persistence if stochastic noise is compatible

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


class StochasticDemographicV5FixedEquation:
    """Stochastic V4 with CORRECT energy equation from Phase 5."""

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

        # Energy gate (sigmoid) - SAME as Phase 5
        energy_gate = 1.0 / (1.0 + np.exp(-0.1 * (rho - rho_threshold)))

        # Composition (birth) rate - SAME as Phase 5
        lambda_c = lambda_0 * energy_gate * phi**2

        # Decomposition (death) rate with crowding - SAME as Phase 5
        crowding = (N / 100.0)**2
        lambda_d = mu_0 * (1.0 + sigma * crowding)

        return lambda_c, lambda_d

    def synchronized_step(self, state: np.ndarray, R: float) -> np.ndarray:
        """Synchronized update with CORRECT energy equation."""
        E, N, phi, theta_rel = state

        # Prevent division by zero
        N = max(1.0, N)
        E = max(0.0, E)
        phi = np.clip(phi, 0.0, 1.0)

        # Energy density
        rho = E / N

        # Extract parameters
        r = self.params['r']
        K = self.params['K']
        alpha = self.params['alpha']
        beta = self.params['beta']
        gamma = self.params['gamma']
        phi_0 = self.params['phi_0']
        omega = self.params['omega']
        kappa_phi = self.params.get('kappa_phi', 0.1)  # For phi dynamics

        # Compute rates
        lambda_c, lambda_d = self.compute_rates(state, R)

        # CORRECTED ENERGY DYNAMICS (from Phase 5 V4)
        dE_dt = (N * r * (1 - rho / K) +
                alpha * N * R -
                beta * N * rho -
                gamma * lambda_c * rho)

        E_new = E + self.dt * dE_dt
        E_new = max(E_new, 0.0)

        # Phi dynamics (corrected from Phase 5)
        dphi_dt = phi_0 - omega * np.sin(theta_rel) - kappa_phi * phi
        phi_new = phi + self.dt * dphi_dt
        phi_new = np.clip(phi_new, 0.0, 1.0)

        # Theta dynamics (relative phase)
        dtheta_rel_dt = 0.01 * (N - 50)
        theta_rel_new = theta_rel + self.dt * dtheta_rel_dt

        # Population dynamics (stochastic)
        if N > 0:
            birth_rate_total = lambda_c * N
            death_rate_total = lambda_d * N
            n_births = np.random.poisson(birth_rate_total * self.dt)
            n_deaths = np.random.poisson(death_rate_total * self.dt)
            N_new = max(N + n_births - n_deaths, 1.0)  # Minimum N=1
        else:
            N_new = 1.0

        return np.array([E_new, N_new, phi_new, theta_rel_new])

    def simulate(
        self,
        t_span: np.ndarray,
        initial_state: np.ndarray,
        R_func: Callable[[float], float]
    ) -> np.ndarray:
        """Simulate stochastic model with corrected equations."""
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


def run_stochastic_ensemble_v5(
    params: Dict,
    initial_state: np.ndarray,
    n_runs: int = 20,
    t_total: float = 5000.0,
    dt: float = 0.1,
    R_value: float = 1.0
) -> Dict:
    """Run ensemble of stochastic simulations (V5 CORRECTED)."""
    print(f"\nRunning stochastic ensemble (V5 CORRECTED EQUATION, n={n_runs}, t={t_total})...")

    t_span = np.arange(0, t_total + dt, dt)
    R_func = lambda t: R_value

    all_trajectories = []

    for run_idx in range(n_runs):
        if (run_idx + 1) % 5 == 0:
            print(f"  Run {run_idx+1}/{n_runs}")

        model = StochasticDemographicV5FixedEquation(params, dt=dt, random_seed=run_idx)
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

    # Check for extinction (N < 2 = extinction for discrete system)
    extinction_count = 0
    for run_idx in range(n_runs):
        if np.mean(all_trajectories[run_idx, -100:, 1]) < 2.0:
            extinction_count += 1

    print(f"\n  Overall mean N: {overall_mean:.2f}")
    print(f"  Overall std N: {overall_std:.2f}")
    print(f"  Overall CV: {overall_cv:.3f} ({overall_cv*100:.1f}%)")
    print(f"  Within-run CV (average): {mean_within_cv:.3f} ({mean_within_cv*100:.1f}%)")
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


def main():
    """Main execution: stochastic V4 with corrected energy equation."""
    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 6: STOCHASTIC V4 (V5 - CORRECTED EQUATION)")
    print("=" * 70)
    print()

    print("CRITICAL FIX: Use correct energy equation from Phase 5 V4")
    print("  OLD (V1-V4): dE/dt = gamma*R - alpha*lambda_c*E - beta*N*E")
    print("  NEW (V5):    dE/dt = N*r*(1-rho/K) + alpha*N*R - beta*N*rho - gamma*lambda_c*rho")
    print()
    print("Missing term in V1-V4: N*r*(1-rho/K) - intrinsic energy generation!")
    print()

    # V4 sustained parameters (from Phase 5)
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
        'kappa_phi': 0.1,
        'phi_0': 0.06,
        'rho_threshold': 5.0
    }

    empirical_cv = 0.092

    # Test with deterministic steady state (from Phase 5)
    print("\n" + "=" * 70)
    print("TEST: Deterministic Steady State with Corrected Equation")
    print("=" * 70)
    initial_state = np.array([2411.77, 215.0, 0.6074, 0.0])

    results = run_stochastic_ensemble_v5(
        params,
        initial_state,
        n_runs=20,
        t_total=5000.0,
        dt=0.1,
        R_value=1.0
    )

    # Summary
    print("\n" + "=" * 70)
    print("STOCHASTIC V4 SUMMARY (V5 - CORRECTED)")
    print("=" * 70)
    print()

    print(f"Paper 2 empirical CV: {empirical_cv:.3f} ({empirical_cv*100:.1f}%)")
    print(f"\nStochastic V5 (corrected equation) results:")
    print(f"  Overall CV (pooled): {results['overall_cv']:.3f} ({results['overall_cv']*100:.1f}%)")
    print(f"  Within-run CV (average): {results['mean_within_cv']:.3f} ({results['mean_within_cv']*100:.1f}%)")
    print(f"  Extinction rate: {results['extinction_count']}/{20} ({results['extinction_count']/20*100:.1f}%)")
    print()

    cv_error_within = abs(results['mean_within_cv'] - empirical_cv)

    if results['extinction_count'] == 0:
        if cv_error_within < 0.02:
            print("✅ HYPOTHESIS VALIDATED")
            print("   Corrected equation enables persistence + CV matches empirical!")
            print(f"   Error: {cv_error_within:.4f} (< 0.02 threshold)")
        elif cv_error_within < 0.05:
            print("✅ HYPOTHESIS PARTIALLY VALIDATED")
            print("   Corrected equation enables persistence, CV close to empirical")
            print(f"   Error: {cv_error_within:.4f} (< 0.05)")
        else:
            print("⚠️ PERSISTENCE ACHIEVED, CV MISMATCH")
            print("   Corrected equation prevents extinction but CV doesn't match")
            print(f"   Error: {cv_error_within:.4f} (> 0.05)")
    elif results['extinction_count'] < 5:
        print("⚠️ PARTIAL SUCCESS")
        print(f"   Only {results['extinction_count']}/20 extinctions (was 20/20 in V1-V4)")
        print("   Corrected equation improves persistence but not complete")
    else:
        print("❌ EQUATION FIX INSUFFICIENT")
        print(f"   Still {results['extinction_count']}/20 extinctions")
        print("   Suggests additional incompatibility beyond energy equation")

    print()


if __name__ == "__main__":
    main()
