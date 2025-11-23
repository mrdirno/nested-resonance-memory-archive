#!/usr/bin/env python3
"""
PAPER 7 PHASE 3: DIRECT DYNAMICAL REGIME CLASSIFICATION

Purpose: Classify system behavior across parameter space without equilibrium analysis

Approach:
- Simulate V2 model to quasi-steady-state for each parameter value
- Compute time-averaged population N* (order parameter)
- Classify regime: sustained, collapse, oscillatory
- Compare to Paper 2 empirical regime boundaries

Motivation:
V2 model has no fixed-point equilibria (by design, consistent with "perpetual motion").
Classical bifurcation analysis requires equilibria. This approach directly characterizes
attractors without equilibrium assumptions.

Date: 2025-10-27 (Cycle 378)
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
from scipy.integrate import odeint

# Import V2 model
import sys
sys.path.insert(0, str(Path(__file__).parent))

try:
    from paper7_v2_constrained_model import NRMDynamicalSystemV2
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    print("WARNING: V2 model not found.")


class RegimeClassifier:
    """Classify dynamical regimes via time series simulation."""

    def __init__(self, ode_system):
        """
        Initialize classifier.

        Args:
            ode_system: NRM ODE system (V2 constrained model)
        """
        self.ode_system = ode_system

    def simulate_to_steady_state(
        self,
        initial_state: np.ndarray,
        R_value: float = 1.0,
        t_transient: float = 500.0,
        t_measure: float = 500.0,
        dt: float = 0.1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate system to quasi-steady-state and measure dynamics.

        Args:
            initial_state: [E_total, N, phi, theta_int]
            R_value: Constant reality input
            t_transient: Transient time to discard
            t_measure: Measurement time window
            dt: Time step

        Returns:
            time_array, trajectory (shape: [n_steps, 4])
        """
        R_func = lambda t: R_value

        # Full time span
        t_total = t_transient + t_measure
        t_array = np.arange(0, t_total, dt)

        # Simulate
        trajectory = self.ode_system.simulate(t_array, initial_state, R_func)

        # Extract measurement window
        n_transient = int(t_transient / dt)
        t_measure_array = t_array[n_transient:]
        trajectory_steady = trajectory[n_transient:]

        return t_measure_array, trajectory_steady

    def classify_regime(
        self,
        trajectory: np.ndarray,
        threshold_sustained: float = 10.0,
        threshold_collapse: float = 3.0,
        oscillation_threshold: float = 0.2
    ) -> Dict:
        """
        Classify regime from steady-state trajectory.

        Args:
            trajectory: State trajectory [n_steps, 4] = [E, N, phi, theta]
            threshold_sustained: N* > this → sustained
            threshold_collapse: N* < this → collapse
            oscillation_threshold: relative_std > this → oscillatory

        Returns:
            classification dict with regime, N_mean, N_std, etc.
        """
        # Extract population
        N_trajectory = trajectory[:, 1]

        # Statistics
        N_mean = np.mean(N_trajectory)
        N_std = np.std(N_trajectory)
        N_min = np.min(N_trajectory)
        N_max = np.max(N_trajectory)

        # Relative variability
        relative_std = N_std / (N_mean + 1e-9)

        # Classify
        if N_mean > threshold_sustained:
            if relative_std > oscillation_threshold:
                regime = 'sustained_oscillatory'
            else:
                regime = 'sustained_stable'
        elif N_mean < threshold_collapse:
            regime = 'collapse'
        else:
            if relative_std > oscillation_threshold:
                regime = 'bistable_oscillatory'
            else:
                regime = 'bistable'

        return {
            'regime': regime,
            'N_mean': float(N_mean),
            'N_std': float(N_std),
            'N_min': float(N_min),
            'N_max': float(N_max),
            'relative_std': float(relative_std),
            'is_sustained': bool(N_mean > threshold_sustained),
            'is_collapse': bool(N_mean < threshold_collapse),
            'is_oscillatory': bool(relative_std > oscillation_threshold)
        }


def run_regime_classification(
    param_name: str,
    param_min: float,
    param_max: float,
    n_points: int = 30,
    output_dir: Path = None,
    t_transient: float = 500.0,
    t_measure: float = 500.0
) -> Dict:
    """
    Run regime classification across parameter range.

    Args:
        param_name: Parameter to vary ('omega', 'K', etc.)
        param_min: Minimum parameter value
        param_max: Maximum parameter value
        n_points: Number of parameter values to test
        output_dir: Directory for saving results
        t_transient: Transient time to discard
        t_measure: Measurement time window

    Returns:
        Results dictionary with regime classifications
    """
    print(f"\n{'=' * 70}")
    print(f"REGIME CLASSIFICATION: {param_name}")
    print(f"{'=' * 70}")
    print(f"Range: [{param_min}, {param_max}]")
    print(f"Points: {n_points}")
    print(f"Transient time: {t_transient}")
    print(f"Measurement time: {t_measure}")
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    if not MODEL_AVAILABLE:
        print("ERROR: V2 model not available. Cannot proceed.")
        return {'error': 'V2 model not found'}

    # Initialize V2 model with parameters favoring sustained dynamics
    params = {
        'r': 0.1,         # Higher recharge rate
        'K': 150.0,       # Higher carrying capacity
        'alpha': 0.2,     # Stronger reality coupling
        'beta': 0.01,     # Lower maintenance cost
        'gamma': 0.1,     # Lower composition cost
        'lambda_0': 2.0,  # Higher base composition rate
        'mu_0': 0.5,      # Lower decomposition rate
        'sigma': 0.05,    # Less crowding penalty
        'omega': 0.02,    # Will be varied
        'kappa': 0.05     # Lower resonance decay
    }

    ode_system = NRMDynamicalSystemV2(params)
    classifier = RegimeClassifier(ode_system)

    # Parameter sweep
    param_values = np.linspace(param_min, param_max, n_points)

    # Initial state (reasonable baseline)
    initial_state = np.array([100.0, 10.0, 0.5, 0.0])  # [E, N, phi, theta]

    # Storage
    results_list = []

    print("Simulating parameter sweep...")
    for i, param_value in enumerate(param_values):
        # Update parameter
        original_value = ode_system.params[param_name]
        ode_system.params[param_name] = param_value

        try:
            # Simulate to steady state
            t_array, trajectory = classifier.simulate_to_steady_state(
                initial_state,
                t_transient=t_transient,
                t_measure=t_measure
            )

            # Classify regime
            classification = classifier.classify_regime(trajectory)

            # Store result
            result = {
                'param_value': float(param_value),
                'regime': classification['regime'],
                'N_mean': classification['N_mean'],
                'N_std': classification['N_std'],
                'N_min': classification['N_min'],
                'N_max': classification['N_max'],
                'relative_std': classification['relative_std'],
                'is_sustained': classification['is_sustained'],
                'is_collapse': classification['is_collapse'],
                'is_oscillatory': classification['is_oscillatory'],
                'success': True
            }

        except Exception as e:
            print(f"  ERROR at {param_name}={param_value:.4f}: {e}")
            result = {
                'param_value': float(param_value),
                'regime': None,
                'N_mean': None,
                'N_std': None,
                'N_min': None,
                'N_max': None,
                'relative_std': None,
                'is_sustained': None,
                'is_collapse': None,
                'is_oscillatory': None,
                'success': False,
                'error': str(e)
            }

        results_list.append(result)

        # Restore original parameter
        ode_system.params[param_name] = original_value

        # Progress indicator
        if (i + 1) % 5 == 0 or (i + 1) == n_points:
            N_display = f"{result['N_mean']:.2f}" if result['N_mean'] is not None else 'FAIL'
            print(f"  Progress: {i+1}/{n_points} points | "
                  f"Latest: {param_name}={param_value:.4f}, "
                  f"N*={N_display}, "
                  f"regime={result['regime']}")

    print()

    # Detect regime boundaries
    print("Detecting regime boundaries...")
    boundaries = detect_regime_boundaries(results_list, param_name)
    print(f"  Detected {len(boundaries)} boundaries:")
    for boundary in boundaries:
        print(f"    {boundary['transition']}: {param_name}={boundary['param_value']:.4f}")
    print()

    # Compile results
    results = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'param_name': param_name,
            'param_range': [float(param_min), float(param_max)],
            'n_points': n_points,
            't_transient': t_transient,
            't_measure': t_measure,
            'model': 'NRMDynamicalSystemV2'
        },
        'classifications': results_list,
        'boundaries': boundaries,
        'parameters_used': params
    }

    # Save results
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / "data" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"paper7_phase3_regime_{param_name}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved: {output_file}")
    print()

    return results


def detect_regime_boundaries(classifications: List[Dict], param_name: str) -> List[Dict]:
    """
    Detect regime transition boundaries.

    Args:
        classifications: List of regime classification dicts
        param_name: Parameter being varied

    Returns:
        List of detected boundaries
    """
    boundaries = []

    for i in range(1, len(classifications)):
        prev = classifications[i-1]
        curr = classifications[i]

        # Skip if either failed
        if not prev['success'] or not curr['success']:
            continue

        # Sustained ↔ Collapse transition
        if prev['is_sustained'] and curr['is_collapse']:
            boundaries.append({
                'type': 'sustained_to_collapse',
                'transition': 'Sustained → Collapse',
                'param_value': (prev['param_value'] + curr['param_value']) / 2
            })
        elif prev['is_collapse'] and curr['is_sustained']:
            boundaries.append({
                'type': 'collapse_to_sustained',
                'transition': 'Collapse → Sustained',
                'param_value': (prev['param_value'] + curr['param_value']) / 2
            })

        # Oscillatory transitions
        if not prev['is_oscillatory'] and curr['is_oscillatory']:
            boundaries.append({
                'type': 'stable_to_oscillatory',
                'transition': 'Stable → Oscillatory',
                'param_value': (prev['param_value'] + curr['param_value']) / 2
            })
        elif prev['is_oscillatory'] and not curr['is_oscillatory']:
            boundaries.append({
                'type': 'oscillatory_to_stable',
                'transition': 'Oscillatory → Stable',
                'param_value': (prev['param_value'] + curr['param_value']) / 2
            })

    return boundaries


def main():
    """Execute Paper 7 Phase 3 regime classification."""

    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 3: REGIME CLASSIFICATION")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # Run regime classification for omega (frequency parameter)
    # This corresponds to Paper 2 empirical frequency parameter
    results_omega = run_regime_classification(
        param_name='omega',
        param_min=0.005,  # Low frequency (0.5% → collapse regime)
        param_max=0.05,   # High frequency (5% → sustained regime)
        n_points=30,      # Moderate resolution
        t_transient=500.0,  # 500 time units transient
        t_measure=500.0     # 500 time units measurement
    )

    print("\n" + "=" * 70)
    print("PHASE 3 REGIME CLASSIFICATION COMPLETE")
    print("=" * 70)
    print("Next steps:")
    print("  - Visualize regime diagram (paper7_phase3_visualization.py or new script)")
    print("  - Compare boundaries to Paper 2 empirical (0.5%, 2.5%)")
    print("  - Run additional parameter sweeps (K, lambda_0, mu_0, alpha)")
    print("  - Integrate findings into Paper 7 manuscript")
    print("=" * 70)


if __name__ == "__main__":
    main()
