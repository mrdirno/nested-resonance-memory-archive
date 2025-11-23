#!/usr/bin/env python3
"""
PAPER 7 PHASE 6: STOCHASTIC DEMOGRAPHIC V4 MODEL (V2 - FIXED)

Purpose: Fix extinction bug in V1 via synchronized state updates

Bug in V1: State update ordering caused mismatch between ODE and Poisson steps
- ODE step updated E, phi based on old N
- Poisson step then updated N based on new E, phi
- Created feedback loop: E grows unbounded → rho diverges → rates become invalid

Fix in V2: Synchronized updates
- Compute rates using current state [E, N, phi]
- Update all variables based on those rates
- Avoid feedback mismatch

Date: 2025-10-31 (Cycle 788)
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


class StochasticDemographicV4Fixed:
    """
    Stochastic extension of V4 with demographic noise (FIXED VERSION).

    Key difference from V1:
    - Synchronized state updates (no feedback mismatch)
    - Compute rates once per timestep using current state
    - Update all variables based on those rates
    """

    def __init__(self, params: Dict, dt: float = 0.1, random_seed: int = None):
        """
        Initialize stochastic demographic V4 model (fixed version).

        Args:
            params: V4 parameters (same as deterministic)
            dt: Time step for integration
            random_seed: Random seed for reproducibility
        """
        self.params = params
        self.dt = dt

        if random_seed is not None:
            np.random.seed(random_seed)

    def compute_rates(self, state: np.ndarray, R: float) -> Tuple[float, float]:
        """
        Compute birth and death rates from current state.

        Args:
            state: Current [E, N, phi, theta_rel]
            R: Resource level

        Returns:
            (lambda_c, lambda_d) birth and death rates per capita
        """
        E, N, phi, theta_rel = state

        # Extract parameters
        lambda_0 = self.params['lambda_0']
        mu_0 = self.params['mu_0']
        sigma = self.params['sigma']
        kappa = self.params['kappa']
        rho_threshold = self.params['rho_threshold']
        K = self.params['K']

        # Prevent division by zero
        if N <= 0:
            return 0.0, 0.0

        # Energy per capita
        rho = E / N

        # Energy gate (sigmoid)
        energy_gate = 1.0 / (1.0 + np.exp(-kappa * (rho - rho_threshold)))

        # Composition (birth) rate
        lambda_c = lambda_0 * energy_gate * phi**2

        # Decomposition (death) rate with crowding
        crowding = (N / K)**2
        lambda_d = mu_0 * (1.0 + sigma * crowding)

        return lambda_c, lambda_d

    def synchronized_step(self, state: np.ndarray, R: float) -> np.ndarray:
        """
        FIXED: Synchronized update of all state variables.

        Key fix: Compute rates ONCE using current state, then update all variables.

        Args:
            state: Current [E, N, phi, theta_rel]
            R: Resource level

        Returns:
            New state after dt
        """
        E, N, phi, theta_rel = state

        # Extract parameters
        r = self.params['r']
        alpha = self.params['alpha']
        beta = self.params['beta']
        gamma = self.params['gamma']
        phi_0 = self.params['phi_0']
        omega = self.params['omega']

        # 1. Compute rates using CURRENT state (before any updates)
        lambda_c, lambda_d = self.compute_rates(state, R)

        # 2. Update continuous variables (E, phi, theta) using those rates

        # Energy dynamics
        dE_dt = gamma * R - alpha * lambda_c * E - beta * N * E
        E_new = E + self.dt * dE_dt
        E_new = max(E_new, 0.0)  # Keep positive

        # Phi dynamics
        dphi_dt = phi_0 * r * (1 - phi) - lambda_c * phi
        phi_new = phi + self.dt * dphi_dt
        phi_new = np.clip(phi_new, 0.0, 1.0)  # Keep in [0,1]

        # Theta dynamics
        theta_rel_new = theta_rel - omega * self.dt

        # 3. Update discrete population using SAME rates
        if N > 0:
            # Total rates (per population)
            birth_rate_total = lambda_c * N
            death_rate_total = lambda_d * N

            # Expected number of events in dt (Poisson distributed)
            n_births = np.random.poisson(birth_rate_total * self.dt)
            n_deaths = np.random.poisson(death_rate_total * self.dt)

            # Update population
            N_new = N + n_births - n_deaths
            N_new = max(N_new, 0)  # Cannot go negative
        else:
            N_new = 0

        return np.array([E_new, N_new, phi_new, theta_rel_new])

    def simulate(
        self,
        t_span: np.ndarray,
        initial_state: np.ndarray,
        R_func: Callable[[float], float]
    ) -> np.ndarray:
        """
        Simulate stochastic demographic V4 model (fixed version).

        Args:
            t_span: Time points to record
            initial_state: Initial [E, N, phi, theta_rel]
            R_func: Resource function R(t)

        Returns:
            Trajectory array (len(t_span) × 4)
        """
        n_steps = len(t_span)
        trajectory = np.zeros((n_steps, 4))
        trajectory[0] = initial_state

        state = initial_state.copy()

        for i in range(1, n_steps):
            t = t_span[i]
            R = R_func(t)

            # FIXED: Synchronized update (compute rates once, update all variables)
            state = self.synchronized_step(state, R)

            trajectory[i] = state

        return trajectory


def run_stochastic_ensemble_fixed(
    params: Dict,
    initial_state: np.ndarray,
    n_runs: int = 20,
    t_total: float = 5000.0,
    dt: float = 0.1,
    R_value: float = 1.0
) -> Dict:
    """
    Run ensemble of stochastic simulations (FIXED VERSION).

    Args:
        params: V4 parameters
        initial_state: Initial state
        n_runs: Number of ensemble members
        t_total: Total simulation time
        dt: Time step
        R_value: Constant resource level

    Returns:
        Ensemble statistics
    """
    print(f"\nRunning stochastic demographic ensemble (FIXED, n={n_runs}, t={t_total})...")

    t_span = np.arange(0, t_total + dt, dt)
    R_func = lambda t: R_value

    # Store all trajectories
    all_trajectories = []

    for run_idx in range(n_runs):
        if (run_idx + 1) % 5 == 0:
            print(f"  Run {run_idx+1}/{n_runs}")

        model = StochasticDemographicV4Fixed(params, dt=dt, random_seed=run_idx)
        trajectory = model.simulate(t_span, initial_state, R_func)
        all_trajectories.append(trajectory)

    all_trajectories = np.array(all_trajectories)  # (n_runs, n_steps, 4)

    # Calculate ensemble statistics (exclude transient: t > 500)
    transient_idx = int(500.0 / dt)

    # Extract steady-state population from all runs
    N_steady = all_trajectories[:, transient_idx:, 1]  # (n_runs, n_steady_steps)

    # Statistics across ensemble
    mean_N_ensemble = []
    std_N_ensemble = []

    for run_idx in range(n_runs):
        N_run = N_steady[run_idx]
        mean_N_ensemble.append(np.mean(N_run))
        std_N_ensemble.append(np.std(N_run))

    mean_N_ensemble = np.array(mean_N_ensemble)
    std_N_ensemble = np.array(std_N_ensemble)

    # Overall statistics
    overall_mean = np.mean(mean_N_ensemble)
    overall_std = np.std(N_steady.flatten())  # Pool all data points
    overall_cv = overall_std / overall_mean if overall_mean > 0 else 0.0

    # Within-run CV (average across runs)
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

    return {
        'trajectories': all_trajectories,
        't_span': t_span,
        'overall_mean': overall_mean,
        'overall_std': overall_std,
        'overall_cv': overall_cv,
        'mean_within_cv': mean_within_cv,
        'within_run_cv': within_run_cv,
        'mean_N_ensemble': mean_N_ensemble,
        'std_N_ensemble': std_N_ensemble
    }


def plot_stochastic_results_fixed(results: Dict, empirical_cv: float, output_dir: Path):
    """Generate publication-quality figure for stochastic results (FIXED)."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    trajectories = results['trajectories']
    t_span = results['t_span']

    # Panel A: Population trajectories (first 5 runs)
    ax = axes[0, 0]
    for run_idx in range(min(5, len(trajectories))):
        N_traj = trajectories[run_idx, :, 1]
        ax.plot(t_span, N_traj, alpha=0.6, linewidth=1)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population (N)')
    ax.set_title('A. Population Trajectories (Sample)')
    ax.grid(True, alpha=0.3)

    # Panel B: Energy trajectories
    ax = axes[0, 1]
    for run_idx in range(min(5, len(trajectories))):
        E_traj = trajectories[run_idx, :, 0]
        ax.plot(t_span, E_traj, alpha=0.6, linewidth=1)
    ax.set_xlabel('Time')
    ax.set_ylabel('Energy (E)')
    ax.set_title('B. Energy Trajectories (Sample)')
    ax.grid(True, alpha=0.3)

    # Panel C: Ensemble statistics
    ax = axes[1, 0]
    mean_N = np.mean(trajectories[:, :, 1], axis=0)
    std_N = np.std(trajectories[:, :, 1], axis=0)
    ax.plot(t_span, mean_N, 'b-', linewidth=2, label='Mean N')
    ax.fill_between(t_span, mean_N - std_N, mean_N + std_N, alpha=0.3, label='±1 SD')
    ax.set_xlabel('Time')
    ax.set_ylabel('Population (N)')
    ax.set_title('C. Ensemble Statistics')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Panel D: CV comparison
    ax = axes[1, 1]
    cv_data = [results['overall_cv'], results['mean_within_cv'], empirical_cv]
    labels = ['Overall\nCV', 'Within-run\nCV (mean)', 'Paper 2\nEmpirical']
    colors = ['steelblue', 'coral', 'green']
    bars = ax.bar(labels, cv_data, color=colors, alpha=0.7)
    ax.set_ylabel('Coefficient of Variation')
    ax.set_title('D. CV Comparison')
    ax.axhline(empirical_cv, color='green', linestyle='--', alpha=0.5, label='Target')
    ax.grid(True, alpha=0.3, axis='y')

    # Add values on bars
    for bar, val in zip(bars, cv_data):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val*100:.1f}%', ha='center', va='bottom')

    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paper7_phase6_stochastic_FIXED_{timestamp}.png"
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\nGenerating stochastic demographic figure (FIXED)...")
    print(f"  Saved: {filepath}")


def main():
    """Main execution: stochastic demographic V4 (FIXED VERSION)."""
    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 6: STOCHASTIC DEMOGRAPHIC V4 (V2 - FIXED)")
    print("=" * 70)
    print()

    print("Fix: Synchronized state updates (no feedback mismatch)")
    print("Hypothesis: Poisson birth/death maintains CV ≈ 9.2% (Paper 2 empirical)")
    print()

    # V4 sustained parameters
    base_params = {
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

    # Test: Deterministic steady state (E~2400, N~215)
    print("\n" + "=" * 70)
    print("TEST: Start at Deterministic Steady State (E~2400, N~215)")
    print("=" * 70)
    print("(From Phase 5: final state at t=10,000)")
    initial_state_steady = np.array([2411.77, 215.0, 0.6074, 0.0])  # From Phase 5

    results = run_stochastic_ensemble_fixed(
        base_params,
        initial_state_steady,
        n_runs=20,
        t_total=5000.0,
        dt=0.1,
        R_value=1.0
    )

    # Visualize
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_stochastic_results_fixed(results, empirical_cv, output_dir)

    # Summary
    print("\n" + "=" * 70)
    print("STOCHASTIC DEMOGRAPHIC V4 SUMMARY (FIXED)")
    print("=" * 70)
    print()

    print(f"Paper 2 empirical CV: {empirical_cv:.3f} ({empirical_cv*100:.1f}%)")
    print(f"\nStochastic V4 (FIXED) results:")
    print(f"  Overall CV (pooled): {results['overall_cv']:.3f} ({results['overall_cv']*100:.1f}%)")
    print(f"  Within-run CV (average): {results['mean_within_cv']:.3f} ({results['mean_within_cv']*100:.1f}%)")
    print()

    # Test hypothesis
    cv_error_overall = abs(results['overall_cv'] - empirical_cv)
    cv_error_within = abs(results['mean_within_cv'] - empirical_cv)

    if cv_error_within < 0.02:  # Within 2 percentage points
        print("✅ HYPOTHESIS VALIDATED")
        print("   Demographic noise produces persistent CV matching empirical!")
        print(f"   Error: {cv_error_within:.4f} (< 0.02 threshold)")
    elif cv_error_within < 0.05:
        print("⚠️ HYPOTHESIS PARTIALLY SUPPORTED")
        print("   Demographic noise maintains variance, but not exact match")
        print(f"   Error: {cv_error_within:.4f} (< 0.05)")
    else:
        print("❌ HYPOTHESIS REJECTED")
        print("   Demographic noise does not match empirical CV")
        print(f"   Error: {cv_error_within:.4f} (> 0.05)")

    print()


if __name__ == "__main__":
    main()
