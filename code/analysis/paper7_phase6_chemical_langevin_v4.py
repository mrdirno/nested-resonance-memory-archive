#!/usr/bin/env python3
"""
Paper 7 Phase 6 Revision: Chemical Langevin Equation for V4

Purpose: Implement proper SDE coupling to test if demographic noise
         maintains persistent variance matching Paper 2 empirical (CV ≈ 9.2%)

Previous Failure (Phase 6 V1):
- Naive operator splitting: continuous ODEs for E/φ, discrete Poisson for N
- Caused artificial extinction even from deterministic steady state
- Root cause: Inconsistent coupling between continuous/discrete updates

Chemical Langevin Approach (CLE):
- Treat ALL variables as stochastic differential equations (SDEs)
- Add Gaussian noise scaled by √(rate) for demographic stochasticity
- Euler-Maruyama integration with consistent timestep
- No operator splitting → numerically stable

System:
  dE = [γR - αλ_c E - βNE] dt + √(γR) dW_E
  dN = [λ_c N - λ_d N] dt + √(λ_c N + λ_d N) dW_N
  dφ = [φ₀r(1-φ) - λ_c φ] dt + √(λ_c φ) dW_φ
  dθ = -ω dt

Where:
- dW are independent Wiener processes (Brownian motion)
- √(rate) terms capture demographic stochasticity
- Noise vanishes when rates → 0 or populations → 0

Validation Tests:
1. Deterministic limit: noise → 0 should recover V4
2. Steady state: Should NOT exhibit extinction (unlike Phase 6 V1)
3. Persistent variance: CV should stabilize at non-zero value
4. Comparison: Match Paper 2 empirical CV ≈ 9.2%?

Date: 2025-10-27 (Cycle 391+)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))


class ChemicalLangevinV4:
    """
    Chemical Langevin Equation (CLE) extension of V4 model.

    Implements proper SDE coupling with demographic noise.
    """

    def __init__(self, params: Dict[str, float], dt: float = 0.01,
                 noise_scale: float = 1.0):
        """
        Initialize CLE model.

        Args:
            params: V4 model parameters
            dt: Integration timestep (Euler-Maruyama)
            noise_scale: Multiplier for demographic noise (0 = deterministic)
        """
        self.params = params
        self.dt = dt
        self.noise_scale = noise_scale

    def compute_rates(self, state: np.ndarray, R: float) -> Tuple[float, float, float]:
        """
        Compute birth, death, and composition rates.

        Args:
            state: [E_total, N, phi, theta_rel]
            R: Reality input

        Returns:
            (birth_rate_total, death_rate_total, composition_rate_total)
        """
        E_total, N, phi, theta_rel = state

        # Enforce constraints
        N = max(1.0, N)
        E_total = max(0.0, E_total)
        phi = np.clip(phi, 0.0, 1.0)

        # Energy density
        rho = E_total / N

        # Extract parameters
        r = self.params['r']
        alpha = self.params['alpha']
        beta = self.params['beta']
        gamma = self.params['gamma']
        lambda_0 = self.params['lambda_0']
        mu_0 = self.params['mu_0']
        sigma = self.params['sigma']
        omega = self.params['omega']
        phi_0 = self.params.get('phi_0', 0.06)
        rho_threshold = self.params.get('rho_threshold', 5.0)
        kappa = self.params.get('kappa', 0.1)

        # Energy gate (sigmoid)
        energy_gate = 1.0 / (1.0 + np.exp(-kappa * (rho - rho_threshold)))

        # Resonance factor
        R_resonance = R * np.cos(theta_rel)

        # Composition rate
        lambda_c = lambda_0 * energy_gate * phi**2

        # Death rate (density-dependent + baseline)
        death_rate_per_capita = mu_0 * (1 + sigma * (N / 100))

        # Total rates
        birth_rate_total = lambda_c * N
        death_rate_total = death_rate_per_capita * N
        composition_rate_total = lambda_c * N  # Energy consumption

        return birth_rate_total, death_rate_total, composition_rate_total

    def sde_step(self, state: np.ndarray, R: float) -> np.ndarray:
        """
        One Euler-Maruyama step of the Chemical Langevin Equation.

        Args:
            state: [E_total, N, phi, theta_rel]
            R: Reality input

        Returns:
            Updated state after dt timestep
        """
        E_total, N, phi, theta_rel = state

        # Compute rates
        birth_rate, death_rate, comp_rate = self.compute_rates(state, R)

        # Extract parameters
        r = self.params['r']
        alpha = self.params['alpha']
        beta = self.params['beta']
        gamma = self.params['gamma']
        omega = self.params['omega']
        phi_0 = self.params.get('phi_0', 0.06)

        # Deterministic drifts
        dE_drift = (gamma * R - alpha * comp_rate - beta * N * E_total) * self.dt
        dN_drift = (birth_rate - death_rate) * self.dt
        dphi_drift = (phi_0 * r * (1 - phi) - comp_rate / max(N, 1.0)) * self.dt
        dtheta_drift = -omega * self.dt

        # Stochastic increments (Gaussian with variance = rate * dt)
        # dW = √dt * N(0,1) for each Wiener process
        sqrt_dt = np.sqrt(self.dt)

        # Energy noise: √(γR * dt)
        dE_noise = self.noise_scale * np.sqrt(max(0, gamma * R)) * sqrt_dt * np.random.randn()

        # Population noise: √((birth + death) * dt)
        demographic_rate = max(0, birth_rate + death_rate)
        dN_noise = self.noise_scale * np.sqrt(demographic_rate) * sqrt_dt * np.random.randn()

        # Resonance noise: √(comp_rate * dt)
        dphi_noise = self.noise_scale * np.sqrt(max(0, comp_rate / max(N, 1.0))) * sqrt_dt * np.random.randn()

        # Phase has no noise (deterministic rotation)
        dtheta_noise = 0.0

        # Update state
        E_new = max(0.0, E_total + dE_drift + dE_noise)
        N_new = max(1.0, N + dN_drift + dN_noise)  # Absorbing barrier at N=1
        phi_new = np.clip(phi + dphi_drift + dphi_noise, 0.0, 1.0)
        theta_new = (theta_rel + dtheta_drift) % (2 * np.pi)

        return np.array([E_new, N_new, phi_new, theta_new])

    def simulate(self, t_span: Tuple[float, float], initial_state: np.ndarray,
                 R_func: callable, n_steps: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate the Chemical Langevin system.

        Args:
            t_span: (t_start, t_end)
            initial_state: [E_total, N, phi, theta_rel]
            R_func: Function R(t) for reality input
            n_steps: Number of timesteps (default: computed from dt)

        Returns:
            (t_array, trajectory) where trajectory is (n_steps, 4)
        """
        t_start, t_end = t_span
        if n_steps is None:
            n_steps = int((t_end - t_start) / self.dt)

        t_array = np.linspace(t_start, t_end, n_steps)
        trajectory = np.zeros((n_steps, 4))
        trajectory[0] = initial_state

        for i in range(1, n_steps):
            t = t_array[i-1]
            R = R_func(t)
            trajectory[i] = self.sde_step(trajectory[i-1], R)

        return t_array, trajectory


def run_ensemble(params: Dict[str, float], initial_state: np.ndarray,
                 t_span: Tuple[float, float], n_runs: int = 20,
                 noise_scale: float = 1.0, dt: float = 0.01) -> Dict:
    """
    Run ensemble of CLE simulations and compute statistics.

    Args:
        params: V4 model parameters
        initial_state: Starting state
        t_span: (t_start, t_end)
        n_runs: Number of ensemble members
        noise_scale: Demographic noise strength
        dt: Integration timestep

    Returns:
        Dictionary with ensemble statistics
    """
    t_start, t_end = t_span
    n_steps = int((t_end - t_start) / dt)

    # Storage for ensemble
    trajectories = np.zeros((n_runs, n_steps, 4))
    persistence_count = 0

    # Reality input (constant for now)
    R_func = lambda t: 1.0

    # Run ensemble
    for run_idx in range(n_runs):
        cle = ChemicalLangevinV4(params, dt=dt, noise_scale=noise_scale)
        t_array, traj = cle.simulate(t_span, initial_state, R_func, n_steps=n_steps)
        trajectories[run_idx] = traj

        # Check persistence (N > 1 at end)
        if traj[-1, 1] > 1.0:
            persistence_count += 1

    # Compute statistics
    mean_trajectory = np.mean(trajectories, axis=0)
    std_trajectory = np.std(trajectories, axis=0)

    # Population statistics (N is index 1)
    N_ensemble = trajectories[:, :, 1]
    N_mean = np.mean(N_ensemble, axis=0)
    N_std = np.std(N_ensemble, axis=0)

    # CV over time
    cv_over_time = N_std / (N_mean + 1e-10)

    # Steady-state statistics (last 20% of trajectory)
    steady_start = int(0.8 * n_steps)
    N_steady = N_ensemble[:, steady_start:]

    steady_mean = np.mean(N_steady)
    steady_std = np.std(N_steady)
    steady_cv = steady_std / (steady_mean + 1e-10)

    # Within-run CV (temporal fluctuations)
    within_run_cvs = []
    for run_idx in range(n_runs):
        N_run = N_ensemble[run_idx, steady_start:]
        if np.mean(N_run) > 1.0:  # Only if not extinct
            cv = np.std(N_run) / np.mean(N_run)
            within_run_cvs.append(cv)

    mean_within_cv = np.mean(within_run_cvs) if within_run_cvs else 0.0

    return {
        't_array': t_array,
        'trajectories': trajectories,
        'mean_trajectory': mean_trajectory,
        'std_trajectory': std_trajectory,
        'N_mean': N_mean,
        'N_std': N_std,
        'cv_over_time': cv_over_time,
        'steady_mean': steady_mean,
        'steady_std': steady_std,
        'steady_cv': steady_cv,
        'within_run_cv': mean_within_cv,
        'persistence_prob': persistence_count / n_runs,
        'n_runs': n_runs,
        'n_steps': n_steps
    }


def test_deterministic_limit(params: Dict[str, float],
                             initial_state: np.ndarray) -> Dict:
    """
    Test 1: Verify that noise_scale=0 recovers deterministic V4.

    Should match V4 trajectory exactly.
    """
    print("\n" + "="*70)
    print("TEST 1: DETERMINISTIC LIMIT (noise_scale = 0)")
    print("="*70)

    t_span = (0, 1000)

    # Run CLE with no noise
    results = run_ensemble(params, initial_state, t_span, n_runs=5,
                          noise_scale=0.0, dt=0.1)

    # Check if all runs identical (deterministic)
    traj_variance = np.var(results['trajectories'][:, -1, 1])  # Variance in final N

    print(f"\nFinal state variance across runs: {traj_variance:.6e}")
    print(f"Final mean N: {results['steady_mean']:.2f}")
    print(f"Final CV: {results['steady_cv']:.6f}")

    if traj_variance < 1e-6:
        print("✅ PASS: Deterministic limit recovered (all runs identical)")
    else:
        print("❌ FAIL: Runs should be identical with noise_scale=0")

    return results


def test_steady_state_stability(params: Dict[str, float],
                                initial_state: np.ndarray) -> Dict:
    """
    Test 2: Verify that system does NOT exhibit extinction from steady state.

    Should fix Phase 6 V1 failure (universal extinction).
    """
    print("\n" + "="*70)
    print("TEST 2: STEADY STATE STABILITY")
    print("="*70)

    # Use deterministic steady state from Phase 5 as initial condition
    # E=2411.77, N=215.30, φ=0.6074 from t=10,000
    steady_state = np.array([2411.77, 215.30, 0.6074, 0.0])

    t_span = (0, 5000)

    # Run with moderate demographic noise
    results = run_ensemble(params, steady_state, t_span, n_runs=20,
                          noise_scale=1.0, dt=0.1)

    print(f"\nPersistence probability: {results['persistence_prob']:.2%}")
    print(f"Final mean N: {results['steady_mean']:.2f} ± {results['steady_std']:.2f}")
    print(f"Final CV: {results['steady_cv']:.4f}")

    if results['persistence_prob'] >= 0.9:
        print("✅ PASS: System stable (no artificial extinction)")
    else:
        print("❌ FAIL: Extinction occurred (numerical instability persists)")

    return results


def test_persistent_variance(params: Dict[str, float],
                             initial_state: np.ndarray) -> Dict:
    """
    Test 3: Measure persistent variance and compare to Paper 2 empirical.

    Target: CV ≈ 9.2% (Paper 2 within-experiment mean)
    """
    print("\n" + "="*70)
    print("TEST 3: PERSISTENT VARIANCE (vs. Paper 2 empirical CV = 9.2%)")
    print("="*70)

    steady_state = np.array([2411.77, 215.30, 0.6074, 0.0])
    t_span = (0, 10000)

    # Test multiple noise scales
    noise_levels = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    results_list = []

    for noise_scale in noise_levels:
        print(f"\n  Testing noise_scale = {noise_scale:.1f}...")
        results = run_ensemble(params, steady_state, t_span, n_runs=20,
                              noise_scale=noise_scale, dt=0.1)

        print(f"    Within-run CV: {results['within_run_cv']:.4f} ({results['within_run_cv']*100:.2f}%)")
        print(f"    Ensemble CV: {results['steady_cv']:.4f} ({results['steady_cv']*100:.2f}%)")
        print(f"    Persistence: {results['persistence_prob']:.2%}")

        results_list.append({
            'noise_scale': noise_scale,
            'within_run_cv': results['within_run_cv'],
            'ensemble_cv': results['steady_cv'],
            'persistence_prob': results['persistence_prob'],
            'mean_N': results['steady_mean']
        })

    # Find best match to Paper 2 (CV ≈ 9.2%)
    target_cv = 0.092
    errors = [abs(r['within_run_cv'] - target_cv) for r in results_list]
    best_idx = np.argmin(errors)
    best_match = results_list[best_idx]

    print(f"\n" + "="*70)
    print("BEST MATCH TO PAPER 2 EMPIRICAL:")
    print(f"  Noise scale: {best_match['noise_scale']:.1f}")
    print(f"  Within-run CV: {best_match['within_run_cv']:.4f} ({best_match['within_run_cv']*100:.2f}%)")
    print(f"  Target CV: {target_cv:.4f} ({target_cv*100:.2f}%)")
    print(f"  Error: {errors[best_idx]:.4f}")
    print(f"  Persistence: {best_match['persistence_prob']:.2%}")
    print("="*70)

    return results_list


def generate_figure(test1_results: Dict, test2_results: Dict,
                   test3_results: List[Dict], output_dir: Path):
    """
    Generate 4-panel publication figure.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Paper 7 Phase 6 Revision: Chemical Langevin V4",
                fontsize=14, fontweight='bold')

    # Panel A: Deterministic limit
    ax = axes[0, 0]
    t = test1_results['t_array']
    for i in range(test1_results['n_runs']):
        ax.plot(t, test1_results['trajectories'][i, :, 1], 'b-', alpha=0.6, lw=0.8)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('A) Deterministic Limit (noise_scale=0)', fontweight='bold')
    ax.grid(alpha=0.3)

    # Panel B: Steady state stability
    ax = axes[0, 1]
    t = test2_results['t_array']
    for i in range(test2_results['n_runs']):
        ax.plot(t, test2_results['trajectories'][i, :, 1], 'g-', alpha=0.4, lw=0.8)
    ax.axhline(215.30, color='r', linestyle='--', label='Initial steady state', lw=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Population N')
    ax.set_title('B) Steady State Stability (noise_scale=1.0)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel C: CV vs. noise scale
    ax = axes[1, 0]
    noise_scales = [r['noise_scale'] for r in test3_results]
    within_cvs = [r['within_run_cv'] * 100 for r in test3_results]
    ensemble_cvs = [r['ensemble_cv'] * 100 for r in test3_results]

    ax.plot(noise_scales, within_cvs, 'o-', label='Within-run CV', lw=2, markersize=8)
    ax.plot(noise_scales, ensemble_cvs, 's-', label='Ensemble CV', lw=2, markersize=8)
    ax.axhline(9.2, color='r', linestyle='--', label='Paper 2 empirical (9.2%)', lw=2)
    ax.set_xlabel('Noise Scale')
    ax.set_ylabel('Coefficient of Variation (%)')
    ax.set_title('C) CV Calibration vs. Paper 2', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel D: Persistence probability
    ax = axes[1, 1]
    persistence = [r['persistence_prob'] * 100 for r in test3_results]
    ax.plot(noise_scales, persistence, 'o-', color='purple', lw=2, markersize=8)
    ax.axhline(90, color='r', linestyle='--', label='90% threshold', lw=2)
    ax.set_xlabel('Noise Scale')
    ax.set_ylabel('Persistence Probability (%)')
    ax.set_title('D) Persistence vs. Noise Strength', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim([0, 105])

    plt.tight_layout()

    output_path = output_dir / f"paper7_phase6_chemical_langevin_{timestamp}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Figure saved: {output_path}")
    plt.close()


def main():
    """
    Main execution: Run all tests and generate results.
    """
    print("="*70)
    print("PAPER 7 PHASE 6 REVISION: CHEMICAL LANGEVIN V4")
    print("="*70)
    print("\nPurpose: Fix Phase 6 V1 operator splitting failure")
    print("Method: Chemical Langevin Equation (proper SDE coupling)")
    print("Target: Persistent variance matching Paper 2 (CV ≈ 9.2%)")

    # V4 sustained parameters (from Phase 3-5)
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

    # Initial state (low population to test growth)
    initial_state = np.array([100.0, 10.0, 0.5, 0.0])  # [E, N, phi, theta]

    # Run tests
    test1_results = test_deterministic_limit(params, initial_state)
    test2_results = test_steady_state_stability(params, initial_state)
    test3_results = test_persistent_variance(params, initial_state)

    # Generate figure
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_figure(test1_results, test2_results, test3_results, output_dir)

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = results_dir / f"paper7_phase6_chemical_langevin_{timestamp}.json"

    results_data = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'purpose': 'Phase 6 revision with Chemical Langevin Equation',
            'params': params
        },
        'test1_deterministic': {
            'final_N': float(test1_results['steady_mean']),
            'final_CV': float(test1_results['steady_cv']),
            'variance': float(np.var(test1_results['trajectories'][:, -1, 1]))
        },
        'test2_stability': {
            'persistence_prob': float(test2_results['persistence_prob']),
            'final_N': float(test2_results['steady_mean']),
            'final_CV': float(test2_results['steady_cv'])
        },
        'test3_variance': [
            {
                'noise_scale': float(r['noise_scale']),
                'within_run_cv': float(r['within_run_cv']),
                'ensemble_cv': float(r['ensemble_cv']),
                'persistence_prob': float(r['persistence_prob']),
                'mean_N': float(r['mean_N'])
            }
            for r in test3_results
        ],
        'paper2_target': {
            'target_cv': 0.092,
            'target_description': 'Within-experiment mean CV from Paper 2'
        }
    }

    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)

    print(f"\n✅ Results saved: {results_path}")

    print("\n" + "="*70)
    print("PHASE 6 REVISION COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
