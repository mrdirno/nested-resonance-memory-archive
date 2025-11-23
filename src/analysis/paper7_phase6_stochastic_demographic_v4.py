#!/usr/bin/env python3
"""
PAPER 7 PHASE 6: STOCHASTIC DEMOGRAPHIC V4 MODEL

Purpose: Add demographic noise (Poisson birth/death) to deterministic V4

Phase 4-5 discovered deterministic V4 has vanishing variance (CV → 0 as t → ∞),
while Paper 2 empirical shows persistent variance (CV = 9.2%).

Hypothesis: Demographic stochasticity maintains persistent variance.

Implementation:
- Hybrid deterministic-stochastic model
- Continuous ODE for E, phi (large populations)
- Discrete Poisson events for N (birth/death)
- Rates from deterministic V4: λ_c(E,N,phi), λ_d(N)

Test:
- Run stochastic V4 for t=5000
- Measure steady-state CV (after transient)
- Compare to Paper 2 empirical CV = 9.2%
- Check if demographic noise produces persistent variance

Date: 2025-10-27 (Cycle 390)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Callable
from scipy.integrate import odeint
import sys

sys.path.append(str(Path(__file__).parent))


class StochasticDemographicV4:
    """
    Stochastic extension of V4 with demographic noise.

    Hybrid model:
    - E, phi evolve deterministically (continuous ODEs)
    - N evolves stochastically (Poisson birth/death events)
    - Rates derived from deterministic V4
    """

    def __init__(self, params: Dict, dt: float = 0.1, random_seed: int = None):
        """
        Initialize stochastic demographic V4 model.

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
        phi_0 = self.params['phi_0']
        rho_threshold = self.params['rho_threshold']

        # Energy per capita
        rho = E / N if N > 0 else 0.0

        # Energy gate (sigmoid)
        energy_gate = 1.0 / (1.0 + np.exp(-kappa * (rho - rho_threshold)))

        # Composition (birth) rate
        lambda_c = lambda_0 * energy_gate * phi**2

        # Decomposition (death) rate with crowding
        crowding = (N / K)**2
        lambda_d = mu_0 * (1.0 + sigma * crowding)

        return lambda_c, lambda_d

    def ode_step(self, state: np.ndarray, R: float) -> np.ndarray:
        """
        One time step of continuous variables (E, phi) using Euler method.

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
        lambda_0 = self.params['lambda_0']
        phi_0 = self.params['phi_0']
        omega = self.params['omega']
        kappa = self.params['kappa']
        rho_threshold = self.params['rho_threshold']

        # Compute rates
        lambda_c, lambda_d = self.compute_rates(state, R)

        # Energy dynamics (continuous ODE)
        dE_dt = gamma * R - alpha * lambda_c * E - beta * N * E
        E_new = E + self.dt * dE_dt
        E_new = max(E_new, 0.0)  # Keep positive

        # Phi dynamics (continuous ODE)
        dphi_dt = phi_0 * r * (1 - phi) - lambda_c * phi
        phi_new = phi + self.dt * dphi_dt
        phi_new = np.clip(phi_new, 0.0, 1.0)  # Keep in [0,1]

        # Theta dynamics (continuous, always rotating)
        theta_rel_new = theta_rel - omega * self.dt

        return np.array([E_new, N, phi_new, theta_rel_new])

    def poisson_step(self, state: np.ndarray, R: float) -> int:
        """
        One time step of discrete population (N) using Gillespie algorithm.

        Args:
            state: Current [E, N, phi, theta_rel]
            R: Resource level

        Returns:
            New N after stochastic birth/death events
        """
        E, N, phi, theta_rel = state

        if N <= 0:
            return 0

        # Compute per-capita rates
        lambda_c, lambda_d = self.compute_rates(state, R)

        # Total rates (per population)
        birth_rate_total = lambda_c * N
        death_rate_total = lambda_d * N

        # Expected number of events in dt (Poisson distributed)
        n_births = np.random.poisson(birth_rate_total * self.dt)
        n_deaths = np.random.poisson(death_rate_total * self.dt)

        # Update population
        N_new = N + n_births - n_deaths
        N_new = max(N_new, 0)  # Cannot go negative

        return N_new

    def simulate(
        self,
        t_span: np.ndarray,
        initial_state: np.ndarray,
        R_func: Callable[[float], float]
    ) -> np.ndarray:
        """
        Simulate stochastic demographic V4 model.

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

            # Update continuous variables (E, phi, theta_rel)
            state = self.ode_step(state, R)

            # Update discrete population (N)
            N_new = self.poisson_step(state, R)
            state[1] = N_new

            trajectory[i] = state

        return trajectory


def run_stochastic_ensemble(
    params: Dict,
    initial_state: np.ndarray,
    n_runs: int = 20,
    t_total: float = 5000.0,
    dt: float = 0.1,
    R_value: float = 1.0
) -> Dict:
    """
    Run ensemble of stochastic simulations.

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
    print(f"\\nRunning stochastic demographic ensemble (n={n_runs}, t={t_total})...")

    t_span = np.arange(0, t_total + dt, dt)
    R_func = lambda t: R_value

    # Store all trajectories
    all_trajectories = []

    for run_idx in range(n_runs):
        if (run_idx + 1) % 5 == 0:
            print(f"  Run {run_idx+1}/{n_runs}")

        model = StochasticDemographicV4(params, dt=dt, random_seed=run_idx)
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

    print(f"\\n  Overall mean N: {overall_mean:.2f}")
    print(f"  Overall std N: {overall_std:.2f}")
    print(f"  Overall CV: {overall_cv:.3f} ({overall_cv*100:.1f}%)")
    print(f"  Within-run CV (average): {mean_within_cv:.3f} ({mean_within_cv*100:.1f}%)")

    return {
        't_span': t_span,
        'all_trajectories': all_trajectories,
        'mean_N_ensemble': mean_N_ensemble,
        'std_N_ensemble': std_N_ensemble,
        'overall_mean': overall_mean,
        'overall_std': overall_std,
        'overall_cv': overall_cv,
        'within_run_cv': within_run_cv,
        'mean_within_cv': mean_within_cv,
        'n_runs': n_runs,
        'transient_idx': transient_idx
    }


def plot_stochastic_results(results: Dict, empirical_cv: float, output_dir: Path):
    """
    Visualize stochastic demographic results.

    Args:
        results: Ensemble results
        empirical_cv: Target empirical CV
        output_dir: Output directory
    """
    print("\\nGenerating stochastic demographic figure...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    t = results['t_span']
    trajectories = results['all_trajectories']
    n_runs = results['n_runs']

    # Panel 1: Sample trajectories
    ax = axes[0, 0]
    for i in range(min(10, n_runs)):  # Show first 10
        N = trajectories[i, :, 1]
        ax.plot(t, N, alpha=0.5, linewidth=0.5)
    ax.axvline(500, color='red', linestyle='--', alpha=0.5, label='Transient end')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Population (N)', fontsize=11)
    ax.set_title(f'Sample Trajectories (n={min(10, n_runs)})', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Panel 2: Ensemble statistics
    ax = axes[0, 1]

    # Mean ± std across ensemble at each time point
    N_mean = np.mean(trajectories[:, :, 1], axis=0)
    N_std = np.std(trajectories[:, :, 1], axis=0)

    ax.plot(t, N_mean, 'k-', linewidth=2, label='Ensemble mean')
    ax.fill_between(t, N_mean - N_std, N_mean + N_std, alpha=0.3, label='± 1 std')
    ax.axvline(500, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Population (N)', fontsize=11)
    ax.set_title('Ensemble Mean ± Std', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    # Panel 3: Within-run CV distribution
    ax = axes[1, 0]
    within_cv = results['within_run_cv']

    ax.hist(within_cv, bins=15, alpha=0.7, edgecolor='black')
    ax.axvline(empirical_cv, color='red', linestyle='--', linewidth=2, label=f'Paper 2 empirical = {empirical_cv:.3f}')
    ax.axvline(results['mean_within_cv'], color='blue', linestyle='-', linewidth=2, label=f'Stochastic V4 mean = {results["mean_within_cv"]:.3f}')
    ax.set_xlabel('CV (within-run)', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Within-Run CV Distribution', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3, axis='y')

    # Panel 4: Comparison to empirical
    ax = axes[1, 1]

    cv_values = [results['overall_cv'], results['mean_within_cv'], empirical_cv]
    labels = ['Overall\n(pooled)', 'Within-run\n(average)', 'Paper 2\nempirical']
    colors = ['blue', 'green', 'red']

    bars = ax.bar(labels, cv_values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.set_ylabel('Coefficient of Variation', fontsize=11)
    ax.set_title('CV Comparison: Stochastic V4 vs. Empirical', fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, val in zip(bars, cv_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{val:.3f}\n({val*100:.1f}%)',
               ha='center', va='bottom', fontsize=10, fontweight='bold')

    fig.suptitle('Paper 7 Phase 6: Stochastic Demographic V4',
                fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = output_dir / f"paper7_phase6_stochastic_demographic_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def main():
    """Main execution: stochastic demographic V4."""
    print("\\n" + "=" * 70)
    print("PAPER 7 PHASE 6: STOCHASTIC DEMOGRAPHIC V4")
    print("=" * 70)
    print()

    print("Goal: Add demographic noise to V4 to produce persistent variance")
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

    # Test 1: Small initial population (N=10) - expect extinction
    print("\\n" + "=" * 70)
    print("TEST 1: Small Initial Population (N=10)")
    print("=" * 70)
    initial_state_small = np.array([100.0, 10.0, 0.5, 0.0])

    results_small = run_stochastic_ensemble(
        base_params,
        initial_state_small,
        n_runs=20,
        t_total=2000.0,  # Shorter to see extinction dynamics
        dt=0.1,
        R_value=1.0
    )

    # Test 2: Deterministic steady state (E~2400, N~215) - expect persistence
    print("\\n" + "=" * 70)
    print("TEST 2: Start at Deterministic Steady State (E~2400, N~215)")
    print("=" * 70)
    print("(From Phase 5: final state at t=10,000)")
    initial_state_steady = np.array([2411.77, 215.0, 0.6074, 0.0])  # From Phase 5

    results_steady = run_stochastic_ensemble(
        base_params,
        initial_state_steady,
        n_runs=20,
        t_total=5000.0,
        dt=0.1,
        R_value=1.0
    )

    # Use steady state results for main analysis
    results = results_steady

    # Visualize
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_stochastic_results(results, empirical_cv, output_dir)

    # Summary
    print("\\n" + "=" * 70)
    print("STOCHASTIC DEMOGRAPHIC V4 SUMMARY")
    print("=" * 70)
    print()

    print(f"Paper 2 empirical CV: {empirical_cv:.3f} ({empirical_cv*100:.1f}%)")
    print(f"\\nStochastic V4 results:")
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
