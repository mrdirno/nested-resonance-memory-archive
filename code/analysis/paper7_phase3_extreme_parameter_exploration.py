#!/usr/bin/env python3
"""
PAPER 7 PHASE 3: EXTREME PARAMETER EXPLORATION

Purpose: Find regime boundaries by testing extreme parameter values

Motivation:
- Cycle 381 bifurcation analysis: 97% equilibrium success, zero bifurcations
- V4 model remarkably stable across standard ranges
- Need extreme values to find collapse boundaries
- Compare to Paper 2 empirical regime boundaries (0.5%, 2.5%)

Strategy:
- Test very low/high omega (rotation frequency)
- Test extreme rho_threshold (energy gate)
- Test extreme phi_0 (resonance source)
- Test extreme lambda_0, mu_0 (composition/decomposition rates)
- Use regime classification to detect collapse vs. sustained

Date: 2025-10-27 (Cycle 382)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json
import sys

sys.path.append(str(Path(__file__).parent))

from paper7_v4_energy_threshold import NRMDynamicalSystemV4


class RegimeClassifierV4:
    """Classify V4 model dynamics as sustained, oscillatory, or collapsed."""

    def __init__(self, model: NRMDynamicalSystemV4):
        """
        Initialize regime classifier for V4 model.

        Args:
            model: V4 NRM model instance
        """
        self.model = model

    def simulate_long_term(
        self,
        initial_state: np.ndarray,
        R_func: callable,
        t_total: float = 2000.0,
        t_measure: float = 500.0,
        dt: float = 0.1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate system to steady state and measure final dynamics.

        Args:
            initial_state: Initial condition [E, N, phi, theta_rel]
            R_func: Reality forcing function
            t_total: Total simulation time
            t_measure: Duration to measure at end
            dt: Time step

        Returns:
            (full_trajectory, measurement_window)
        """
        # Full simulation
        t_span = np.arange(0, t_total, dt)
        trajectory = self.model.simulate(t_span, initial_state, R_func)

        # Measurement window (final portion)
        n_measure = int(t_measure / dt)
        measurement = trajectory[-n_measure:]

        return trajectory, measurement

    def classify_regime(
        self,
        measurement: np.ndarray,
        threshold_sustained: float = 10.0,
        threshold_collapse: float = 3.0,
        oscillation_threshold: float = 0.2
    ) -> Dict:
        """
        Classify regime from measurement window.

        Args:
            measurement: Trajectory segment [time, 4] (E, N, phi, theta_rel)
            threshold_sustained: N > threshold → sustained
            threshold_collapse: N < threshold → collapsed
            oscillation_threshold: std(N)/mean(N) > threshold → oscillatory

        Returns:
            Dictionary with regime classification
        """
        N_values = measurement[:, 1]
        N_mean = np.mean(N_values)
        N_std = np.std(N_values)
        N_min = np.min(N_values)
        N_max = np.max(N_values)

        # Coefficient of variation
        cv = N_std / N_mean if N_mean > 0 else np.inf

        # Classification
        if N_mean < threshold_collapse:
            regime = "collapsed"
        elif N_mean > threshold_sustained:
            if cv > oscillation_threshold:
                regime = "oscillatory"
            else:
                regime = "sustained"
        else:
            regime = "intermediate"

        return {
            'regime': regime,
            'N_mean': N_mean,
            'N_std': N_std,
            'N_min': N_min,
            'N_max': N_max,
            'cv': cv
        }


class ExtremeParameterExplorer:
    """Explore extreme parameter ranges to find regime boundaries."""

    def __init__(self, base_params: Dict[str, float]):
        """
        Initialize extreme parameter explorer.

        Args:
            base_params: Base V4 parameter set
        """
        self.base_params = base_params.copy()

    def parameter_sweep_regime(
        self,
        param_name: str,
        param_values: np.ndarray,
        initial_state: np.ndarray,
        R_value: float = 1.0
    ) -> Dict:
        """
        Sweep parameter and classify regime at each value.

        Args:
            param_name: Parameter to vary
            param_values: Array of parameter values
            initial_state: Initial condition
            R_value: Constant reality input

        Returns:
            Dictionary with regime classifications
        """
        results = {
            'param_name': param_name,
            'param_values': [],
            'regimes': [],
            'N_mean': [],
            'N_std': [],
            'cv': []
        }

        R_func = lambda t: R_value

        for param_value in param_values:
            print(f"  Testing {param_name} = {param_value:.4f}...", end='')

            # Update parameter
            params = self.base_params.copy()
            params[param_name] = param_value

            try:
                # Create model
                model = NRMDynamicalSystemV4(params)
                classifier = RegimeClassifierV4(model)

                # Simulate
                _, measurement = classifier.simulate_long_term(
                    initial_state, R_func, t_total=2000.0, t_measure=500.0
                )

                # Classify
                classification = classifier.classify_regime(measurement)

                results['param_values'].append(param_value)
                results['regimes'].append(classification['regime'])
                results['N_mean'].append(classification['N_mean'])
                results['N_std'].append(classification['N_std'])
                results['cv'].append(classification['cv'])

                print(f" {classification['regime']} (N={classification['N_mean']:.2f})")

            except Exception as e:
                print(f" ERROR: {e}")
                results['param_values'].append(param_value)
                results['regimes'].append('error')
                results['N_mean'].append(np.nan)
                results['N_std'].append(np.nan)
                results['cv'].append(np.nan)

        return results

    def find_regime_boundary(
        self,
        results: Dict,
        regime_from: str = 'sustained',
        regime_to: str = 'collapsed'
    ) -> List[float]:
        """
        Find parameter values where regime transitions occur.

        Args:
            results: Results from parameter_sweep_regime
            regime_from: Starting regime
            regime_to: Ending regime

        Returns:
            List of boundary parameter values
        """
        boundaries = []
        regimes = results['regimes']
        param_values = results['param_values']

        for i in range(len(regimes) - 1):
            if regimes[i] == regime_from and regimes[i + 1] == regime_to:
                # Boundary between param_values[i] and param_values[i+1]
                boundaries.append((param_values[i] + param_values[i + 1]) / 2)

        return boundaries


def main():
    """Execute extreme parameter exploration."""
    print("\n" + "=" * 70)
    print("V4 MODEL: EXTREME PARAMETER EXPLORATION")
    print("=" * 70)
    print()
    print("Goal: Find regime boundaries where V4 transitions from sustained to collapsed")
    print()

    # Base V4 parameters
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

    initial_state = np.array([100.0, 10.0, 0.5, 0.0])
    explorer = ExtremeParameterExplorer(params)

    # Output directory
    output_dir = Path(__file__).parent.parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    # 1. EXTREME OMEGA (Very low to very high)
    print("1. EXTREME OMEGA SWEEP")
    print("   Testing: 0.001 to 0.15 (very low to very high)")
    omega_values = np.concatenate([
        np.linspace(0.001, 0.01, 10),  # Very low
        np.linspace(0.01, 0.05, 10),   # Standard
        np.linspace(0.05, 0.15, 10)    # Very high
    ])
    results_omega = explorer.parameter_sweep_regime('omega', omega_values, initial_state)
    all_results.append(results_omega)
    print()

    # 2. EXTREME RHO_THRESHOLD (Energy gate)
    print("2. EXTREME RHO_THRESHOLD SWEEP")
    print("   Testing: 0.5 to 50 (very low to very high)")
    rho_values = np.concatenate([
        np.linspace(0.5, 2.0, 5),      # Very low
        np.linspace(2.0, 10.0, 10),    # Low to medium
        np.linspace(10.0, 50.0, 10)    # High to very high
    ])
    results_rho = explorer.parameter_sweep_regime('rho_threshold', rho_values, initial_state)
    all_results.append(results_rho)
    print()

    # 3. EXTREME PHI_0 (Resonance source)
    print("3. EXTREME PHI_0 SWEEP")
    print("   Testing: 0.005 to 0.2 (very low to high)")
    phi0_values = np.concatenate([
        np.linspace(0.005, 0.03, 10),  # Very low
        np.linspace(0.03, 0.1, 10),    # Low to medium
        np.linspace(0.1, 0.2, 5)       # High
    ])
    results_phi0 = explorer.parameter_sweep_regime('phi_0', phi0_values, initial_state)
    all_results.append(results_phi0)
    print()

    # 4. EXTREME LAMBDA_0 (Composition rate)
    print("4. EXTREME LAMBDA_0 SWEEP")
    print("   Testing: 0.5 to 6.0 (very low to very high)")
    lambda_values = np.concatenate([
        np.linspace(0.5, 1.5, 10),     # Very low
        np.linspace(1.5, 4.0, 10),     # Standard
        np.linspace(4.0, 6.0, 5)       # High
    ])
    results_lambda = explorer.parameter_sweep_regime('lambda_0', lambda_values, initial_state)
    all_results.append(results_lambda)
    print()

    # 5. EXTREME MU_0 (Decomposition rate)
    print("5. EXTREME MU_0 SWEEP")
    print("   Testing: 0.1 to 1.0 (very low to very high)")
    mu_values = np.concatenate([
        np.linspace(0.1, 0.3, 10),     # Very low
        np.linspace(0.3, 0.6, 10),     # Standard
        np.linspace(0.6, 1.0, 5)       # High
    ])
    results_mu = explorer.parameter_sweep_regime('mu_0', mu_values, initial_state)
    all_results.append(results_mu)
    print()

    # Summary
    print("=" * 70)
    print("EXTREME PARAMETER EXPLORATION COMPLETE")
    print("=" * 70)
    print()
    print("Regime Boundaries Detected:")
    for results in all_results:
        param_name = results['param_name']
        boundaries_sc = explorer.find_regime_boundary(results, 'sustained', 'collapsed')
        boundaries_si = explorer.find_regime_boundary(results, 'sustained', 'intermediate')
        boundaries_ic = explorer.find_regime_boundary(results, 'intermediate', 'collapsed')

        print(f"\n{param_name}:")
        if boundaries_sc:
            print(f"  Sustained → Collapsed: {boundaries_sc}")
        if boundaries_si:
            print(f"  Sustained → Intermediate: {boundaries_si}")
        if boundaries_ic:
            print(f"  Intermediate → Collapsed: {boundaries_ic}")

        # Regime counts
        regimes = results['regimes']
        n_sustained = regimes.count('sustained')
        n_collapsed = regimes.count('collapsed')
        n_intermediate = regimes.count('intermediate')
        n_oscillatory = regimes.count('oscillatory')
        n_error = regimes.count('error')

        print(f"  Regime counts: sustained={n_sustained}, collapsed={n_collapsed}, "
              f"intermediate={n_intermediate}, oscillatory={n_oscillatory}, error={n_error}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_path = output_dir / "results" / f"paper7_phase3_extreme_parameters_{timestamp}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    results_json = {
        'timestamp': timestamp,
        'base_params': params,
        'sweeps': []
    }

    for results in all_results:
        results_json['sweeps'].append({
            'param_name': results['param_name'],
            'param_values': results['param_values'],
            'regimes': results['regimes'],
            'N_mean': results['N_mean'],
            'N_std': results['N_std'],
            'cv': results['cv']
        })

    with open(results_path, 'w') as f:
        json.dump(results_json, f, indent=2)

    print(f"\nResults saved: {results_path}")
    print()


if __name__ == "__main__":
    main()
