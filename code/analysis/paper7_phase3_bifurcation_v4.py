#!/usr/bin/env python3
"""
PAPER 7 PHASE 3: BIFURCATION ANALYSIS ON V4 MODEL

Purpose: Map V4 parameter space, identify bifurcations, validate against empirical regimes

Methods:
- Continuation algorithm: Trace equilibrium branches as parameters vary
- Stability analysis: Jacobian eigenvalues determine stable/unstable regions
- Automated bifurcation detection: Identify stability changes, equilibrium disappearance
- Parameter sweeps: omega (rotation frequency) as primary bifurcation parameter

Expected Outcomes:
- Bifurcations identified in omega parameter space
- Predicted boundaries align with Paper 2 empirical regimes (0.5%, 2.5% ±0.5%)
- Stability regions mapped
- Publication figures (bifurcation diagrams, stability maps)

Date: 2025-10-27 (Cycle 381)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
from scipy.optimize import root
from scipy.integrate import odeint
import sys

sys.path.append(str(Path(__file__).parent))

try:
    from paper7_v4_energy_threshold import NRMDynamicalSystemV4
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    print("ERROR: V4 model not found. Cannot proceed.")
    sys.exit(1)


class EquilibriumSolverV4:
    """Find equilibrium points of V4 NRM ODE system."""

    def __init__(self, model: NRMDynamicalSystemV4):
        """
        Initialize equilibrium solver for V4 model.

        Args:
            model: V4 NRM model instance
        """
        self.model = model

    def equilibrium_condition(
        self,
        state: np.ndarray,
        R_value: float = 1.0
    ) -> np.ndarray:
        """
        Equilibrium condition: dstate/dt = 0.

        Args:
            state: [E_total, N, phi, theta_rel]
            R_value: Constant reality input

        Returns:
            derivatives (should be zero at equilibrium)
        """
        R_func = lambda t: R_value
        dstate_dt = self.model.ode_system_v4(state, t=0, R_func=R_func)
        return dstate_dt

    def find_equilibrium(
        self,
        initial_guess: np.ndarray,
        R_value: float = 1.0,
        method: str = 'hybr'
    ) -> Tuple[Optional[np.ndarray], bool, float]:
        """
        Find equilibrium near initial guess.

        Args:
            initial_guess: Starting point [E, N, phi, theta_rel]
            R_value: Constant reality input
            method: Root-finding method

        Returns:
            (equilibrium_state, success, max_residual)
        """
        result = root(
            lambda state: self.equilibrium_condition(state, R_value),
            x0=initial_guess,
            method=method
        )

        if result.success:
            residual = np.abs(self.equilibrium_condition(result.x, R_value))
            max_residual = np.max(residual)
            converged = max_residual < 1e-6

            if converged:
                return result.x, True, max_residual
            else:
                return None, False, max_residual
        else:
            return None, False, np.inf


class StabilityAnalyzerV4:
    """Analyze stability of V4 equilibria via Jacobian eigenvalues."""

    def __init__(self, model: NRMDynamicalSystemV4):
        """
        Initialize stability analyzer for V4 model.

        Args:
            model: V4 NRM model instance
        """
        self.model = model

    def compute_jacobian_numerical(
        self,
        equilibrium_state: np.ndarray,
        R_value: float = 1.0,
        epsilon: float = 1e-6
    ) -> np.ndarray:
        """
        Compute Jacobian matrix numerically via finite differences.

        Args:
            equilibrium_state: Equilibrium point [E, N, phi, theta_rel]
            R_value: Constant reality input
            epsilon: Finite difference step size

        Returns:
            4x4 Jacobian matrix
        """
        R_func = lambda t: R_value
        n_dim = 4
        jacobian = np.zeros((n_dim, n_dim))

        # Base derivatives
        f0 = self.model.ode_system_v4(equilibrium_state, t=0, R_func=R_func)

        # Finite differences for each variable
        for i in range(n_dim):
            state_plus = equilibrium_state.copy()
            state_plus[i] += epsilon
            f_plus = self.model.ode_system_v4(state_plus, t=0, R_func=R_func)
            jacobian[:, i] = (f_plus - f0) / epsilon

        return jacobian

    def analyze_stability(
        self,
        equilibrium_state: np.ndarray,
        R_value: float = 1.0
    ) -> Dict:
        """
        Analyze stability of equilibrium point.

        Args:
            equilibrium_state: Equilibrium point
            R_value: Constant reality input

        Returns:
            Dictionary with eigenvalues, stability classification
        """
        jacobian = self.compute_jacobian_numerical(equilibrium_state, R_value)
        eigenvalues = np.linalg.eigvals(jacobian)

        # Stability classification
        real_parts = eigenvalues.real
        max_real_part = np.max(real_parts)

        if max_real_part < -1e-6:
            stability = "stable"
        elif max_real_part > 1e-6:
            stability = "unstable"
        else:
            stability = "marginal"

        # Check for oscillatory behavior (complex eigenvalues)
        has_complex = np.any(np.abs(eigenvalues.imag) > 1e-6)

        return {
            'eigenvalues': eigenvalues,
            'max_real_part': max_real_part,
            'stability': stability,
            'has_complex': has_complex,
            'jacobian': jacobian
        }


class BifurcationAnalyzerV4:
    """Perform continuation-based bifurcation analysis on V4 model."""

    def __init__(self, base_params: Dict[str, float]):
        """
        Initialize bifurcation analyzer.

        Args:
            base_params: Base parameter set for V4 model
        """
        self.base_params = base_params.copy()

    def parameter_sweep_1d(
        self,
        param_name: str,
        param_range: np.ndarray,
        initial_guess: np.ndarray,
        R_value: float = 1.0
    ) -> Dict:
        """
        Perform 1D parameter sweep, tracking equilibria and stability.

        Args:
            param_name: Parameter to vary (e.g., 'omega')
            param_range: Array of parameter values
            initial_guess: Starting equilibrium guess
            R_value: Constant reality input

        Returns:
            Dictionary with results
        """
        results = {
            'param_name': param_name,
            'param_values': [],
            'equilibria': [],
            'stability': [],
            'eigenvalues': [],
            'found': [],
            'bifurcations_detected': []
        }

        current_guess = initial_guess.copy()
        prev_stability = None

        for param_value in param_range:
            # Update parameter
            params = self.base_params.copy()
            params[param_name] = param_value

            # Create model with updated parameter
            model = NRMDynamicalSystemV4(params)
            solver = EquilibriumSolverV4(model)
            stability_analyzer = StabilityAnalyzerV4(model)

            # Find equilibrium
            eq_state, success, residual = solver.find_equilibrium(
                current_guess, R_value
            )

            results['param_values'].append(param_value)
            results['found'].append(success)

            if success:
                results['equilibria'].append(eq_state)

                # Analyze stability
                stability_info = stability_analyzer.analyze_stability(eq_state, R_value)
                results['stability'].append(stability_info['stability'])
                results['eigenvalues'].append(stability_info['eigenvalues'])

                # Detect bifurcation (stability change)
                if prev_stability is not None and prev_stability != stability_info['stability']:
                    results['bifurcations_detected'].append({
                        'param_value': param_value,
                        'type': f"{prev_stability} -> {stability_info['stability']}"
                    })

                prev_stability = stability_info['stability']

                # Update guess for continuation
                current_guess = eq_state.copy()
            else:
                results['equilibria'].append(None)
                results['stability'].append(None)
                results['eigenvalues'].append(None)

                # Bifurcation detected (equilibrium disappeared)
                if prev_stability is not None:
                    results['bifurcations_detected'].append({
                        'param_value': param_value,
                        'type': 'equilibrium_lost'
                    })
                    prev_stability = None

        return results

    def generate_bifurcation_diagram(
        self,
        results: Dict,
        save_path: Optional[Path] = None
    ) -> None:
        """
        Generate bifurcation diagram from sweep results.

        Args:
            results: Results from parameter_sweep_1d
            save_path: Path to save figure
        """
        param_values = np.array(results['param_values'])
        equilibria = results['equilibria']
        stability = results['stability']

        # Extract N values (population size)
        N_stable = []
        N_unstable = []
        param_stable = []
        param_unstable = []

        for i, eq in enumerate(equilibria):
            if eq is not None:
                param_val = param_values[i]
                N_val = eq[1]  # N is second component

                if stability[i] == 'stable':
                    N_stable.append(N_val)
                    param_stable.append(param_val)
                elif stability[i] == 'unstable':
                    N_unstable.append(N_val)
                    param_unstable.append(param_val)

        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))

        if N_stable:
            ax.plot(param_stable, N_stable, 'b-', linewidth=2, label='Stable')
        if N_unstable:
            ax.plot(param_unstable, N_unstable, 'r--', linewidth=2, label='Unstable')

        # Mark bifurcations
        for bif in results['bifurcations_detected']:
            ax.axvline(
                bif['param_value'],
                color='k',
                linestyle=':',
                alpha=0.5,
                label=f"Bifurcation: {bif['type']}"
            )

        ax.set_xlabel(f"{results['param_name']}", fontsize=12)
        ax.set_ylabel("Population (N)", fontsize=12)
        ax.set_title(f"Bifurcation Diagram: {results['param_name']} Parameter Sweep", fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Bifurcation diagram saved: {save_path}")

        plt.close()


def main():
    """Execute V4 bifurcation analysis."""
    print("\n" + "=" * 70)
    print("V4 MODEL BIFURCATION ANALYSIS")
    print("=" * 70)
    print()

    # V4 parameters (from V4 model success)
    params = {
        'r': 0.15,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 2.5,
        'mu_0': 0.4,
        'sigma': 0.1,
        'omega': 0.02,  # Will be varied
        'kappa': 0.1,
        'phi_0': 0.06,
        'rho_threshold': 5.0
    }

    print("Base parameters:")
    for key, val in params.items():
        print(f"  {key}: {val}")
    print()

    # Create analyzer
    analyzer = BifurcationAnalyzerV4(params)

    # Initial equilibrium guess (from V4 success)
    initial_guess = np.array([521.70, 50.00, 0.5092, 0.4715])
    print(f"Initial equilibrium guess: E={initial_guess[0]:.2f}, N={initial_guess[1]:.2f}, "
          f"phi={initial_guess[2]:.4f}, theta_rel={initial_guess[3]:.4f}")
    print()

    # Omega parameter sweep (rotation frequency)
    print("Omega parameter sweep:")
    print("  Range: 0.005 to 0.05 (50 points)")
    omega_range = np.linspace(0.005, 0.05, 50)

    results = analyzer.parameter_sweep_1d(
        param_name='omega',
        param_range=omega_range,
        initial_guess=initial_guess,
        R_value=1.0
    )

    # Summary
    equilibria_found = np.sum(results['found'])
    print(f"  Equilibria found: {equilibria_found}/{len(omega_range)}")
    print(f"  Bifurcations detected: {len(results['bifurcations_detected'])}")
    print()

    if results['bifurcations_detected']:
        print("Bifurcation points:")
        for bif in results['bifurcations_detected']:
            print(f"  omega = {bif['param_value']:.4f}: {bif['type']}")
        print()

    # Generate bifurcation diagram
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    save_path = output_dir / f"paper7_phase3_bifurcation_v4_omega_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    analyzer.generate_bifurcation_diagram(results, save_path)

    # Save results to JSON
    results_path = output_dir.parent / "results" / f"paper7_phase3_bifurcation_v4_omega_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to JSON-serializable format
    results_json = {
        'param_name': results['param_name'],
        'param_values': results['param_values'],
        'equilibria': [eq.tolist() if eq is not None else None for eq in results['equilibria']],
        'stability': results['stability'],
        'found': results['found'],
        'bifurcations_detected': results['bifurcations_detected']
    }

    with open(results_path, 'w') as f:
        json.dump(results_json, f, indent=2)

    print(f"Results saved: {results_path}")
    print()

    print("=" * 70)
    print("BIFURCATION ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
