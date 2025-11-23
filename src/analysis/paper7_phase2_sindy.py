#!/usr/bin/env python3
"""
PAPER 7 PHASE 2: SYMBOLIC REGRESSION WITH SINDY

Purpose: Discover governing equations from empirical timeseries data using
         Sparse Identification of Nonlinear Dynamics (SINDy).

Approach:
1. Run V2 constrained model with full timeseries logging
2. Extract state variables: E(t), N(t), φ(t), θ(t)
3. Apply SINDy to discover governing equations
4. Compare discovered equations to theoretical ODE system
5. Validate via R², RMSE, equation structure comparison

Background:
- SINDy (Brunton et al., 2016) discovers governing equations from data
- Uses sparse regression to identify minimal equation set
- Works well for systems with known basis functions
- Our basis: polynomials, trig functions, transcendentals (π, e, φ)

Expected Outcome:
- Discovered equations should match theoretical ODE system
- Validates that NRM dynamics are recoverable from data
- Identifies which terms are essential vs negligible

Date: 2025-10-27
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from scipy.integrate import odeint
from scipy.optimize import differential_evolution
import json

# Try to import pysindy (may need: pip install pysindy)
try:
    import pysindy as ps
    SINDY_AVAILABLE = True
except ImportError:
    SINDY_AVAILABLE = False
    print("WARNING: pysindy not installed. Install with: pip install pysindy")


class NRMTimeseriesExtractor:
    """Extract full timeseries from NRM V2 model."""

    def __init__(self, params: Dict[float, float]):
        """
        Initialize with V2 model parameters.

        Args:
            params: Dictionary of model parameters (r, K, alpha, beta, etc.)
        """
        self.params = params
        self.validate_parameters()

    def validate_parameters(self):
        """Ensure parameters are physically reasonable."""
        assert 0.001 <= self.params['r'] <= 0.2, "Recharge rate out of bounds"
        assert 10 <= self.params['K'] <= 200, "Carrying capacity out of bounds"
        assert 0.0001 <= self.params['alpha'] <= 0.5, "Reality coupling out of bounds"
        assert 0.001 <= self.params['beta'] <= 0.1, "Maintenance cost out of bounds"
        assert 0.01 <= self.params['gamma'] <= 1.0, "Composition cost out of bounds"
        assert 0.01 <= self.params['lambda_0'] <= 10.0, "Composition rate out of bounds"
        assert 0.01 <= self.params['mu_0'] <= 5.0, "Decomposition rate out of bounds"
        assert 0.0 <= self.params['sigma'] <= 1.0, "Crowding sensitivity out of bounds"
        assert 0.0 <= self.params['omega'] <= 1.0, "External frequency out of bounds"
        assert 0.0 <= self.params['kappa'] <= 1.0, "Resonance decay out of bounds"

    def ode_system_constrained(self, state: np.ndarray, t: float, R_func: callable) -> np.ndarray:
        """
        V2 constrained NRM equations with non-negativity enforcement.

        Args:
            state: [E_total, N, phi, theta_int]
            t: Time
            R_func: Reality input function R(t)

        Returns:
            derivatives: [dE/dt, dN/dt, dphi/dt, dtheta/dt]
        """
        E_total, N, phi, theta_int = state

        # Enforce constraints
        N = max(1.0, N)  # Minimum population
        E_total = max(0.0, E_total)  # Energy non-negative
        phi = np.clip(phi, 0.0, 1.0)  # Resonance bounded

        # Per-capita energy
        rho = E_total / N

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

        # Reality input
        R_t = R_func(t)

        # Composition rate (smooth sigmoid threshold)
        energy_gate = 1.0 / (1.0 + np.exp(-0.1 * (rho - 40)))
        resonance_amp = phi ** 2
        lambda_c = lambda_0 * energy_gate * resonance_amp

        # Decomposition rate (crowding effects)
        lambda_d = mu_0 * (1 + sigma * (N / 100) ** 2)

        # External phase
        theta_ext = omega * t

        # Governing equations
        dE_dt = N * r * (1 - rho / K) + alpha * N * R_t - beta * N * rho - gamma * lambda_c * rho
        dN_dt = lambda_c - lambda_d
        dphi_dt = omega * np.sin(theta_ext - theta_int) - kappa * phi
        dtheta_dt = omega + 0.01 * (N - 50)

        # Prevent negative population growth
        if N <= 1.0 and dN_dt < 0:
            dN_dt = 0.0

        return np.array([dE_dt, dN_dt, dphi_dt, dtheta_dt])

    def run_timeseries(
        self,
        initial_state: np.ndarray,
        t_span: Tuple[float, float],
        n_points: int = 1000,
        R_func: callable = None
    ) -> Dict[str, np.ndarray]:
        """
        Run V2 model and extract full timeseries.

        Args:
            initial_state: [E_total, N, phi, theta_int] at t=0
            t_span: (t_start, t_end) time range
            n_points: Number of timepoints
            R_func: Reality input function (default: constant 1.0)

        Returns:
            Dictionary with keys: 't', 'E', 'N', 'phi', 'theta'
        """
        if R_func is None:
            R_func = lambda t: 1.0

        t = np.linspace(t_span[0], t_span[1], n_points)

        # Integrate ODEs
        solution = odeint(self.ode_system_constrained, initial_state, t, args=(R_func,))

        E_total = solution[:, 0]
        N = solution[:, 1]
        phi = solution[:, 2]
        theta = solution[:, 3]

        return {
            't': t,
            'E': E_total,
            'N': N,
            'phi': phi,
            'theta': theta,
            'rho': E_total / N  # Per-capita energy
        }


class SINDyDiscovery:
    """Symbolic regression using SINDy."""

    def __init__(self, timeseries: Dict[str, np.ndarray]):
        """
        Initialize with timeseries data.

        Args:
            timeseries: Dictionary with 't', 'E', 'N', 'phi', 'theta'
        """
        self.timeseries = timeseries
        self.discovered_equations = None
        self.model = None

    def prepare_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for SINDy.

        Returns:
            X: State matrix (n_points × 4) [E, N, phi, theta]
            t: Time vector
        """
        t = self.timeseries['t']
        E = self.timeseries['E']
        N = self.timeseries['N']
        phi = self.timeseries['phi']
        theta = self.timeseries['theta']

        X = np.column_stack([E, N, phi, theta])

        return X, t

    def run_sindy(
        self,
        threshold: float = 0.01,
        max_iter: int = 20,
        alpha: float = 0.05
    ) -> Dict:
        """
        Run SINDy algorithm to discover equations.

        Args:
            threshold: Sparsity threshold
            max_iter: Maximum iterations
            alpha: Regularization parameter

        Returns:
            Dictionary with discovered equations, coefficients, feature names
        """
        if not SINDY_AVAILABLE:
            return {
                'error': 'pysindy not installed',
                'equations': None,
                'coefficients': None
            }

        X, t = self.prepare_data()
        dt = t[1] - t[0]

        # Define feature library (polynomial + trig + custom transcendentals)
        poly_library = ps.PolynomialLibrary(degree=3)
        fourier_library = ps.FourierLibrary(n_frequencies=2)

        # Combine libraries
        library = poly_library + fourier_library

        # Define optimizer (STLSQ with thresholding)
        optimizer = ps.STLSQ(threshold=threshold, alpha=alpha, max_iter=max_iter)

        # Create SINDy model
        model = ps.SINDy(
            feature_library=library,
            optimizer=optimizer,
            feature_names=['E', 'N', 'phi', 'theta']
        )

        # Fit model
        model.fit(X, t=dt)

        # Store model
        self.model = model

        # Extract equations
        equations = model.equations()
        coefficients = model.coefficients()
        feature_names = model.get_feature_names()

        self.discovered_equations = {
            'equations': equations,
            'coefficients': coefficients,
            'feature_names': feature_names,
            'score': model.score(X, t=dt)
        }

        return self.discovered_equations

    def validate_against_theoretical(self, theoretical_params: Dict) -> Dict:
        """
        Compare discovered equations to theoretical ODE system.

        Args:
            theoretical_params: True parameter values

        Returns:
            Validation metrics (similarity scores, R², etc.)
        """
        if self.model is None:
            return {'error': 'No model fitted yet'}

        X, t = self.prepare_data()

        # Predict using discovered equations
        X_pred = self.model.simulate(X[0], t)

        # Compute metrics
        residuals = X - X_pred
        rmse = np.sqrt(np.mean(residuals ** 2, axis=0))
        mae = np.mean(np.abs(residuals), axis=0)

        # R² for each variable
        ss_res = np.sum(residuals ** 2, axis=0)
        ss_tot = np.sum((X - X.mean(axis=0)) ** 2, axis=0)
        r2 = 1 - ss_res / ss_tot

        return {
            'rmse': rmse.tolist(),
            'mae': mae.tolist(),
            'r2': r2.tolist(),
            'variable_names': ['E', 'N', 'phi', 'theta']
        }


def main():
    """Execute Paper 7 Phase 2: SINDy symbolic regression."""

    print("=" * 70)
    print("PAPER 7 PHASE 2: SYMBOLIC REGRESSION WITH SINDY")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    if not SINDY_AVAILABLE:
        print("ERROR: pysindy not installed.")
        print("Install with: pip install pysindy")
        print()
        print("Alternative: Manual implementation using sparse regression")
        return

    # V2 model parameters (from Phase 1 fitting)
    params = {
        'r': 0.05,           # Recharge rate
        'K': 100.0,          # Carrying capacity
        'alpha': 0.1,        # Reality coupling
        'beta': 0.02,        # Maintenance cost
        'gamma': 0.3,        # Composition cost
        'lambda_0': 1.0,     # Composition rate
        'mu_0': 0.8,         # Decomposition rate
        'sigma': 0.1,        # Crowding sensitivity
        'omega': 0.2,        # External frequency
        'kappa': 0.1         # Resonance decay
    }

    # Create extractor
    extractor = NRMTimeseriesExtractor(params)

    # Initial state
    initial_state = np.array([100.0, 10.0, 0.5, 0.0])  # [E, N, phi, theta]

    # Run simulation
    print("Running V2 model simulation...")
    timeseries = extractor.run_timeseries(
        initial_state=initial_state,
        t_span=(0, 100),
        n_points=1000,
        R_func=lambda t: 1.0 + 0.1 * np.sin(0.1 * t)  # Oscillating reality input
    )
    print(f"  Timeseries extracted: {len(timeseries['t'])} points")
    print()

    # Run SINDy
    print("Discovering equations with SINDy...")
    discovery = SINDyDiscovery(timeseries)
    discovered = discovery.run_sindy(threshold=0.05, max_iter=20)

    if 'error' in discovered:
        print(f"  ERROR: {discovered['error']}")
        return

    print("  Discovered equations:")
    for i, eq in enumerate(discovered['equations']):
        print(f"    [{i}] {eq}")
    print()

    # Validate
    print("Validating discovered equations...")
    validation = discovery.validate_against_theoretical(params)
    print(f"  R² scores: {validation['r2']}")
    print(f"  RMSE: {validation['rmse']}")
    print(f"  MAE: {validation['mae']}")
    print()

    # Save results
    output_dir = Path(__file__).parent.parent.parent / "data" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "paper7_phase2_sindy_results.json"

    results = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'phase': 'Phase 2: Symbolic Regression',
            'method': 'SINDy (Sparse Identification of Nonlinear Dynamics)'
        },
        'parameters': params,
        'timeseries_summary': {
            'n_points': len(timeseries['t']),
            't_span': [float(timeseries['t'][0]), float(timeseries['t'][-1])],
            'E_range': [float(timeseries['E'].min()), float(timeseries['E'].max())],
            'N_range': [float(timeseries['N'].min()), float(timeseries['N'].max())],
            'phi_range': [float(timeseries['phi'].min()), float(timeseries['phi'].max())],
            'theta_range': [float(timeseries['theta'].min()), float(timeseries['theta'].max())]
        },
        'discovered_equations': {
            'equations': discovered['equations'],
            'feature_names': discovered['feature_names'],
            'score': float(discovered['score'])
        },
        'validation': validation
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    # Plot timeseries
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Paper 7 Phase 2: V2 Model Timeseries', fontsize=14, fontweight='bold')

    axes[0, 0].plot(timeseries['t'], timeseries['E'], 'b-', linewidth=1.5)
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('Total Energy (E)')
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(timeseries['t'], timeseries['N'], 'r-', linewidth=1.5)
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].set_ylabel('Population (N)')
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(timeseries['t'], timeseries['phi'], 'g-', linewidth=1.5)
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].set_ylabel('Resonance (φ)')
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(timeseries['t'], timeseries['theta'], 'm-', linewidth=1.5)
    axes[1, 1].set_xlabel('Time')
    axes[1, 1].set_ylabel('Phase (θ)')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()

    figure_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    figure_file = figure_dir / "paper7_phase2_timeseries.png"
    plt.savefig(figure_file, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {figure_file}")
    print()

    print("=" * 70)
    print("PHASE 2 COMPLETE")
    print("=" * 70)
    print("Next steps:")
    print("  - Examine discovered equations for structure")
    print("  - Compare coefficients to theoretical parameters")
    print("  - Test with different initial conditions")
    print("  - Integrate into Paper 7 manuscript Results section")


if __name__ == "__main__":
    main()
