#!/usr/bin/env python3
"""
PAPER 7 PHASE 3: BIFURCATION ANALYSIS IMPLEMENTATION

Purpose: Map NRM parameter space, identify bifurcations, validate against empirical regimes

Methods:
- Continuation algorithm: Trace equilibrium branches as parameters vary
- Stability analysis: Jacobian eigenvalues determine stable/unstable regions
- Automated bifurcation detection: Identify stability changes, equilibrium disappearance
- Parameter sweeps: 1D (ω, K, λ₀, μ₀, α) and 2D (ω vs K)

Expected Outcomes:
- 2-3 bifurcations identified in ω parameter
- Predicted boundaries align with Paper 2 empirical regimes (0.5%, 2.5% ±0.5%)
- Sensitivity ranking of parameters
- Publication figures (bifurcation diagrams, stability maps)

Date: 2025-10-27
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
from datetime import datetime
import json
from scipy.optimize import root, fsolve
from scipy.integrate import odeint

# Import Paper 7 Phase 1 V2 model
import sys
sys.path.insert(0, str(Path(__file__).parent))

try:
    from paper7_v2_constrained_model import NRMDynamicalSystemV2
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    print("WARNING: V2 model not found. Will use simplified placeholder.")


class EquilibriumSolver:
    """Find equilibrium points of NRM ODE system."""

    def __init__(self, ode_system):
        """
        Initialize equilibrium solver.

        Args:
            ode_system: NRM ODE system (V2 constrained model)
        """
        self.ode_system = ode_system

    def equilibrium_condition(
        self,
        state: np.ndarray,
        R_value: float = 1.0
    ) -> np.ndarray:
        """
        Equilibrium condition: dstate/dt = 0.

        Args:
            state: [E_total, N, phi, theta_int]
            R_value: Constant reality input

        Returns:
            derivatives (should be zero at equilibrium)
        """
        # Constant reality function
        R_func = lambda t: R_value

        # Compute derivatives
        dstate_dt = self.ode_system.ode_system_constrained(state, t=0, R_func=R_func)

        return dstate_dt

    def find_equilibrium(
        self,
        initial_guess: np.ndarray,
        R_value: float = 1.0,
        method: str = 'hybr'
    ) -> Tuple[Optional[np.ndarray], bool]:
        """
        Find equilibrium near initial guess.

        Args:
            initial_guess: Starting point [E_total, N, phi, theta_int]
            R_value: Constant reality input
            method: scipy.optimize.root method ('hybr', 'lm', etc.)

        Returns:
            equilibrium_state, success flag
        """
        try:
            result = root(
                lambda state: self.equilibrium_condition(state, R_value),
                x0=initial_guess,
                method=method,
                options={'xtol': 1e-8, 'maxfev': 1000}
            )

            if result.success:
                # Validate equilibrium
                residual = np.abs(self.equilibrium_condition(result.x, R_value))
                if np.max(residual) < 1e-6:
                    return result.x, True
                else:
                    return None, False
            else:
                return None, False

        except Exception as e:
            print(f"Equilibrium search failed: {e}")
            return None, False


class StabilityAnalyzer:
    """Analyze stability of equilibrium points via Jacobian eigenvalues."""

    def __init__(self, ode_system):
        """
        Initialize stability analyzer.

        Args:
            ode_system: NRM ODE system
        """
        self.ode_system = ode_system

    def compute_jacobian_numerical(
        self,
        equilibrium_state: np.ndarray,
        R_value: float = 1.0,
        epsilon: float = 1e-6
    ) -> np.ndarray:
        """
        Compute Jacobian matrix numerically via finite differences.

        Args:
            equilibrium_state: [E_total, N, phi, theta_int]
            R_value: Constant reality input
            epsilon: Perturbation size for finite differences

        Returns:
            Jacobian matrix (4×4)
        """
        R_func = lambda t: R_value
        n_dim = len(equilibrium_state)
        jacobian = np.zeros((n_dim, n_dim))

        # Baseline derivatives
        f_baseline = self.ode_system.ode_system_constrained(
            equilibrium_state, t=0, R_func=R_func
        )

        # Perturb each dimension
        for i in range(n_dim):
            state_plus = equilibrium_state.copy()
            state_plus[i] += epsilon

            f_plus = self.ode_system.ode_system_constrained(
                state_plus, t=0, R_func=R_func
            )

            jacobian[:, i] = (f_plus - f_baseline) / epsilon

        return jacobian

    def analyze_stability(
        self,
        equilibrium_state: np.ndarray,
        R_value: float = 1.0
    ) -> Tuple[str, np.ndarray, float]:
        """
        Determine stability via eigenvalue analysis.

        Args:
            equilibrium_state: Equilibrium point
            R_value: Reality input value

        Returns:
            stability_classification, eigenvalues, max_real_part
        """
        # Compute Jacobian
        jacobian = self.compute_jacobian_numerical(equilibrium_state, R_value)

        # Eigenvalue analysis
        eigenvalues = np.linalg.eigvals(jacobian)
        max_real_part = np.max(np.real(eigenvalues))

        # Classify stability
        tolerance = 1e-6
        if max_real_part < -tolerance:
            stability = 'stable'
        elif max_real_part > tolerance:
            stability = 'unstable'
        else:
            stability = 'marginal'  # Bifurcation point

        return stability, eigenvalues, max_real_part


class ContinuationMethod:
    """Continuation algorithm to trace equilibrium branches."""

    def __init__(
        self,
        ode_system,
        equilibrium_solver: EquilibriumSolver,
        stability_analyzer: StabilityAnalyzer
    ):
        """
        Initialize continuation method.

        Args:
            ode_system: NRM ODE system
            equilibrium_solver: Equilibrium finder
            stability_analyzer: Stability analyzer
        """
        self.ode_system = ode_system
        self.eq_solver = equilibrium_solver
        self.stability = stability_analyzer

    def trace_equilibrium_branch(
        self,
        param_name: str,
        param_values: np.ndarray,
        initial_guess: np.ndarray,
        R_value: float = 1.0
    ) -> List[Dict]:
        """
        Trace equilibrium branch as parameter varies.

        Args:
            param_name: Parameter to vary (e.g., 'omega')
            param_values: Array of parameter values
            initial_guess: Initial equilibrium guess
            R_value: Reality input value

        Returns:
            List of equilibrium data dictionaries
        """
        equilibria = []
        current_guess = initial_guess.copy()

        for i, param_value in enumerate(param_values):
            # Update parameter
            original_value = self.ode_system.params[param_name]
            self.ode_system.params[param_name] = param_value

            # Find equilibrium
            eq_state, success = self.eq_solver.find_equilibrium(
                current_guess, R_value
            )

            if success and eq_state is not None:
                # Analyze stability
                stab_class, eigenvals, max_real = self.stability.analyze_stability(
                    eq_state, R_value
                )

                # Store result
                result = {
                    'param_value': float(param_value),
                    'equilibrium': eq_state.tolist(),
                    'E_total': float(eq_state[0]),
                    'N': float(eq_state[1]),
                    'phi': float(eq_state[2]),
                    'theta': float(eq_state[3]),
                    'stability': stab_class,
                    'max_eigenvalue_real': float(max_real),
                    'eigenvalues': [complex(ev) for ev in eigenvals],
                    'success': True
                }

                # Use as next initial guess
                current_guess = eq_state.copy()

            else:
                # Equilibrium not found (possible bifurcation)
                result = {
                    'param_value': float(param_value),
                    'equilibrium': None,
                    'E_total': None,
                    'N': None,
                    'phi': None,
                    'theta': None,
                    'stability': None,
                    'max_eigenvalue_real': None,
                    'eigenvalues': None,
                    'success': False
                }

            equilibria.append(result)

            # Restore original parameter
            self.ode_system.params[param_name] = original_value

            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{len(param_values)} points traced")

        return equilibria


class BifurcationDetector:
    """Detect bifurcation points from equilibrium traces."""

    def detect_bifurcations(
        self,
        equilibria: List[Dict],
        param_name: str
    ) -> List[Dict]:
        """
        Identify bifurcation points automatically.

        Args:
            equilibria: List of equilibrium data
            param_name: Parameter name being varied

        Returns:
            List of detected bifurcations
        """
        bifurcations = []

        for i in range(1, len(equilibria)):
            prev = equilibria[i-1]
            curr = equilibria[i]

            # Skip if either point failed
            if not prev['success'] or not curr['success']:
                continue

            # Stability change → bifurcation
            if prev['stability'] != curr['stability']:
                bifurcations.append({
                    'type': 'stability_change',
                    'param_value': (prev['param_value'] + curr['param_value']) / 2,
                    'prev_stability': prev['stability'],
                    'curr_stability': curr['stability'],
                    'description': f"{prev['stability']} → {curr['stability']}"
                })

            # Large jump in N → transcritical or pitchfork
            if prev['N'] is not None and curr['N'] is not None:
                N_jump = abs(curr['N'] - prev['N'])
                if N_jump > 0.5:  # Threshold
                    bifurcations.append({
                        'type': 'large_jump',
                        'param_value': (prev['param_value'] + curr['param_value']) / 2,
                        'N_jump': float(N_jump),
                        'description': f"Population jump: {prev['N']:.2f} → {curr['N']:.2f}"
                    })

        # Check for equilibrium disappearance
        for i in range(1, len(equilibria)):
            prev = equilibria[i-1]
            curr = equilibria[i]

            if prev['success'] and not curr['success']:
                bifurcations.append({
                    'type': 'equilibrium_disappears',
                    'param_value': float(curr['param_value']),
                    'description': f"Equilibrium lost at {param_name}={curr['param_value']:.4f}"
                })

            if not prev['success'] and curr['success']:
                bifurcations.append({
                    'type': 'equilibrium_appears',
                    'param_value': float(curr['param_value']),
                    'description': f"Equilibrium found at {param_name}={curr['param_value']:.4f}"
                })

        return bifurcations


def run_1d_bifurcation_analysis(
    param_name: str,
    param_min: float,
    param_max: float,
    n_points: int = 50,
    output_dir: Path = None
) -> Dict:
    """
    Run 1D bifurcation analysis for a single parameter.

    Args:
        param_name: Parameter to vary ('omega', 'K', etc.)
        param_min: Minimum parameter value
        param_max: Maximum parameter value
        n_points: Number of points in sweep
        output_dir: Directory for saving results

    Returns:
        Results dictionary with equilibria and bifurcations
    """
    print(f"\n{'=' * 70}")
    print(f"1D BIFURCATION ANALYSIS: {param_name}")
    print(f"{'=' * 70}")
    print(f"Range: [{param_min}, {param_max}]")
    print(f"Points: {n_points}")
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    if not MODEL_AVAILABLE:
        print("ERROR: V2 model not available. Cannot proceed.")
        return {'error': 'V2 model not found'}

    # Initialize V2 model
    params = {
        'r': 0.05,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 1.0,
        'mu_0': 0.8,
        'sigma': 0.1,
        'omega': 0.2,
        'kappa': 0.1
    }

    ode_system = NRMDynamicalSystemV2(params)

    # Initialize tools
    eq_solver = EquilibriumSolver(ode_system)
    stability_analyzer = StabilityAnalyzer(ode_system)
    continuation = ContinuationMethod(ode_system, eq_solver, stability_analyzer)
    bifurcation_detector = BifurcationDetector()

    # Parameter sweep
    param_values = np.linspace(param_min, param_max, n_points)

    # Initial guess (reasonable steady-state)
    initial_guess = np.array([100.0, 10.0, 0.5, 0.0])  # [E, N, phi, theta]

    # Trace equilibrium branch
    print("Tracing equilibrium branch...")
    equilibria = continuation.trace_equilibrium_branch(
        param_name, param_values, initial_guess
    )
    print(f"  Traced {len(equilibria)} points")
    print()

    # Detect bifurcations
    print("Detecting bifurcations...")
    bifurcations = bifurcation_detector.detect_bifurcations(equilibria, param_name)
    print(f"  Detected {len(bifurcations)} bifurcations")

    for bif in bifurcations:
        print(f"    {bif['type']}: {param_name}={bif['param_value']:.4f} - {bif['description']}")
    print()

    # Compile results
    results = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'param_name': param_name,
            'param_range': [float(param_min), float(param_max)],
            'n_points': n_points,
            'model': 'NRMDynamicalSystemV2'
        },
        'equilibria': equilibria,
        'bifurcations': bifurcations,
        'parameters_used': params
    }

    # Save results
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / "data" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"paper7_phase3_bifurcation_{param_name}.json"

    # Convert complex eigenvalues to serializable format
    for eq in results['equilibria']:
        if eq['eigenvalues'] is not None:
            eq['eigenvalues'] = [{'real': ev.real, 'imag': ev.imag} for ev in eq['eigenvalues']]

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved: {output_file}")
    print()

    return results


def main():
    """Execute Paper 7 Phase 3 bifurcation analysis."""

    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 3: BIFURCATION ANALYSIS")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # Run 1D bifurcation analysis for omega (frequency parameter)
    # This corresponds to Paper 2 empirical frequency parameter
    results_omega = run_1d_bifurcation_analysis(
        param_name='omega',
        param_min=0.005,  # Low frequency
        param_max=0.5,    # High frequency
        n_points=50
    )

    print("\n" + "=" * 70)
    print("PHASE 3 BIFURCATION ANALYSIS COMPLETE")
    print("=" * 70)
    print("Next steps:")
    print("  - Visualize bifurcation diagrams (paper7_phase3_visualization.py)")
    print("  - Validate against Paper 2 empirical boundaries (0.5%, 2.5%)")
    print("  - Run additional parameter sweeps (K, lambda_0, mu_0, alpha)")
    print("  - Generate publication figures")
    print("=" * 70)


if __name__ == "__main__":
    main()
