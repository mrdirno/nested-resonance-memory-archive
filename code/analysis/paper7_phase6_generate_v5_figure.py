#!/usr/bin/env python3
"""
PAPER 7 PHASE 6: GENERATE V5 PUBLICATION FIGURE

Purpose: Create publication-quality figure showing V5 breakthrough

Panels:
A. Population trajectories (5 sample runs)
B. Energy trajectories (5 sample runs)
C. Ensemble statistics (mean ± SD)
D. CV comparison (V5 vs empirical)

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

        if N <= 0:
            return 0.0, 0.0

        rho = E / N
        energy_gate = 1.0 / (1.0 + np.exp(-0.1 * (rho - rho_threshold)))
        lambda_c = lambda_0 * energy_gate * phi**2
        crowding = (N / 100.0)**2
        lambda_d = mu_0 * (1.0 + sigma * crowding)

        return lambda_c, lambda_d

    def synchronized_step(self, state: np.ndarray, R: float) -> np.ndarray:
        """Synchronized update with CORRECT energy equation."""
        E, N, phi, theta_rel = state

        N = max(1.0, N)
        E = max(0.0, E)
        phi = np.clip(phi, 0.0, 1.0)

        rho = E / N

        r = self.params['r']
        K = self.params['K']
        alpha = self.params['alpha']
        beta = self.params['beta']
        gamma = self.params['gamma']
        phi_0 = self.params['phi_0']
        omega = self.params['omega']
        kappa_phi = self.params.get('kappa_phi', 0.1)

        lambda_c, lambda_d = self.compute_rates(state, R)

        # CORRECTED ENERGY DYNAMICS
        dE_dt = (N * r * (1 - rho / K) +
                alpha * N * R -
                beta * N * rho -
                gamma * lambda_c * rho)

        E_new = E + self.dt * dE_dt
        E_new = max(E_new, 0.0)

        # Phi dynamics
        dphi_dt = phi_0 - omega * np.sin(theta_rel) - kappa_phi * phi
        phi_new = phi + self.dt * dphi_dt
        phi_new = np.clip(phi_new, 0.0, 1.0)

        # Theta dynamics
        dtheta_rel_dt = 0.01 * (N - 50)
        theta_rel_new = theta_rel + self.dt * dtheta_rel_dt

        # Population dynamics (stochastic)
        if N > 0:
            birth_rate_total = lambda_c * N
            death_rate_total = lambda_d * N
            n_births = np.random.poisson(birth_rate_total * self.dt)
            n_deaths = np.random.poisson(death_rate_total * self.dt)
            N_new = max(N + n_births - n_deaths, 1.0)
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


def generate_v5_figure(
    params: Dict,
    initial_state: np.ndarray,
    n_runs: int = 20,
    t_total: float = 5000.0,
    dt: float = 0.1,
    R_value: float = 1.0,
    empirical_cv: float = 0.092,
    output_dir: Path = None
):
    """Generate publication-quality figure for V5 results."""

    print("\n" + "=" * 70)
    print("GENERATING PAPER 7 PHASE 6 V5 PUBLICATION FIGURE")
    print("=" * 70)
    print()

    print(f"Running {n_runs} stochastic simulations...")

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

    # Calculate statistics
    transient_idx = int(500.0 / dt)
    N_steady = all_trajectories[:, transient_idx:, 1]

    overall_mean = np.mean(N_steady)
    overall_std = np.std(N_steady)
    overall_cv = overall_std / overall_mean

    print(f"\n  Mean N: {overall_mean:.2f}")
    print(f"  Std N: {overall_std:.2f}")
    print(f"  CV: {overall_cv:.3f} ({overall_cv*100:.1f}%)")
    print()

    # Create figure
    print("Creating publication figure...")

    fig = plt.figure(figsize=(14, 10))

    # Panel A: Population trajectories
    ax1 = plt.subplot(2, 2, 1)
    for run_idx in range(min(5, n_runs)):
        N_traj = all_trajectories[run_idx, :, 1]
        ax1.plot(t_span, N_traj, alpha=0.7, linewidth=1.5)
    ax1.set_xlabel('Time', fontsize=12)
    ax1.set_ylabel('Population (N)', fontsize=12)
    ax1.set_title('A. Population Trajectories (Sample Runs)', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(150, 280)

    # Panel B: Energy trajectories
    ax2 = plt.subplot(2, 2, 2)
    for run_idx in range(min(5, n_runs)):
        E_traj = all_trajectories[run_idx, :, 0]
        ax2.plot(t_span, E_traj, alpha=0.7, linewidth=1.5)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.set_ylabel('Energy (E)', fontsize=12)
    ax2.set_title('B. Energy Trajectories (Sample Runs)', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Panel C: Ensemble statistics
    ax3 = plt.subplot(2, 2, 3)
    mean_N = np.mean(all_trajectories[:, :, 1], axis=0)
    std_N = np.std(all_trajectories[:, :, 1], axis=0)
    ax3.plot(t_span, mean_N, 'b-', linewidth=2.5, label=f'Mean N = {overall_mean:.1f}')
    ax3.fill_between(t_span, mean_N - std_N, mean_N + std_N, alpha=0.3,
                     color='blue', label=f'±1 SD (σ = {overall_std:.1f})')
    ax3.axhline(overall_mean, color='blue', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Time', fontsize=12)
    ax3.set_ylabel('Population (N)', fontsize=12)
    ax3.set_title('C. Ensemble Statistics (20 Runs)', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10, loc='upper right')
    ax3.grid(True, alpha=0.3)

    # Panel D: CV comparison
    ax4 = plt.subplot(2, 2, 4)
    cv_data = [overall_cv, empirical_cv]
    labels = ['Stochastic V5\n(Demographic Noise)', 'Paper 2\nEmpirical']
    colors = ['steelblue', 'green']
    bars = ax4.bar(labels, cv_data, color=colors, alpha=0.7, width=0.6)
    ax4.set_ylabel('Coefficient of Variation', fontsize=12)
    ax4.set_title('D. CV Comparison', fontsize=13, fontweight='bold')
    ax4.axhline(empirical_cv, color='green', linestyle='--', alpha=0.5,
               linewidth=2, label='Empirical Target')
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylim(0, 0.12)

    # Add values on bars
    for bar, val in zip(bars, cv_data):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{val*100:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add error annotation
    error = abs(overall_cv - empirical_cv)
    ax4.text(0.5, 0.105, f'Error: {error:.3f} ({error*100:.1f}%)',
            ha='center', fontsize=10, color='red', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()

    # Save figure
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paper7_phase6_V5_breakthrough_{timestamp}.png"
    filepath = output_dir / filename

    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Figure saved: {filepath}")
    print()

    return filepath


def main():
    """Main execution."""
    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 6: V5 PUBLICATION FIGURE GENERATION")
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
        'kappa_phi': 0.1,
        'phi_0': 0.06,
        'rho_threshold': 5.0
    }

    initial_state = np.array([2411.77, 215.0, 0.6074, 0.0])
    empirical_cv = 0.092

    generate_v5_figure(
        params,
        initial_state,
        n_runs=20,
        t_total=5000.0,
        dt=0.1,
        R_value=1.0,
        empirical_cv=empirical_cv
    )

    print("=" * 70)
    print("PUBLICATION FIGURE COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
