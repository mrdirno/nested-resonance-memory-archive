#!/usr/bin/env python3
"""
SDE/Fokker-Planck Framework - Gate 1.1 Implementation
======================================================

Analytical treatment of population dynamics using stochastic differential
equations (SDEs) and Fokker-Planck formulation.

**Purpose:** Extend population dynamics models toward analytical treatment that
explains observed coefficient of variation (CV) to ±10% accuracy across ensembles.

**Gate 1.1 Criteria:**
- SDE formulation for regime transitions
- Fokker-Planck equation derivation
- Analytical prediction of population CV
- Validation: ±10% accuracy on experimental data

**Mathematical Framework:**

Population dynamics as SDE:
    dN = μ(N,t)dt + σ(N,t)dW

Where:
    μ(N,t) = drift coefficient (deterministic dynamics)
    σ(N,t) = diffusion coefficient (stochastic noise)
    dW = Wiener process increment

Fokker-Planck equation for probability density P(N,t):
    ∂P/∂t = -∂/∂N[μ(N,t)P] + (1/2)∂²/∂N²[σ²(N,t)P]

Steady-state solution (∂P/∂t = 0):
    P_ss(N) ∝ exp(∫[2μ(N)/σ²(N)]dN)

Statistical moments from P_ss:
    <N> = ∫N P_ss(N) dN
    <N²> = ∫N² P_ss(N) dN
    CV = sqrt(<N²> - <N>²) / <N>

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import numpy as np
from scipy import integrate
from scipy.integrate import cumulative_trapezoid, trapezoid
import scipy.optimize as optimize
from typing import Callable, Tuple, Dict, Optional, List
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class SDEParameters:
    """Parameters for stochastic differential equation."""
    drift_func: Callable[[float, float], float]  # μ(N,t)
    diffusion_func: Callable[[float, float], float]  # σ(N,t)
    N_min: float = 0.1  # Minimum population
    N_max: float = 100.0  # Maximum population
    t_max: float = 1000.0  # Maximum time
    dt: float = 0.01  # Time step
    metadata: Dict = field(default_factory=dict)


@dataclass
class FokkerPlanckSolution:
    """Solution to Fokker-Planck equation."""
    N_values: np.ndarray  # Population grid
    P_ss: np.ndarray  # Steady-state probability density
    mean_N: float  # <N>
    var_N: float  # Var(N) = <N²> - <N>²
    std_N: float  # Standard deviation
    cv_N: float  # Coefficient of variation = std/<N>
    metadata: Dict = field(default_factory=dict)


class SDESystem:
    """
    Stochastic Differential Equation system for population dynamics.

    Implements SDE formulation:
        dN = μ(N,t)dt + σ(N,t)dW
    """

    def __init__(self, params: SDEParameters):
        """
        Initialize SDE system.

        Args:
            params: SDE parameters including drift and diffusion functions
        """
        self.params = params

    def simulate_trajectory(
        self,
        N0: float,
        t_span: Tuple[float, float],
        n_steps: Optional[int] = None,
        random_seed: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate single SDE trajectory using Euler-Maruyama method.

        Args:
            N0: Initial population
            t_span: (t_start, t_end)
            n_steps: Number of time steps (default: auto from dt)
            random_seed: Random seed for reproducibility

        Returns:
            Tuple of (time_array, population_array)
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        t_start, t_end = t_span

        if n_steps is None:
            n_steps = int((t_end - t_start) / self.params.dt)

        dt = (t_end - t_start) / n_steps

        # Initialize arrays
        t_values = np.linspace(t_start, t_end, n_steps + 1)
        N_values = np.zeros(n_steps + 1)
        N_values[0] = N0

        # Euler-Maruyama integration
        for i in range(n_steps):
            t = t_values[i]
            N = N_values[i]

            # Drift term
            drift = self.params.drift_func(N, t)

            # Diffusion term
            diffusion = self.params.diffusion_func(N, t)

            # Wiener increment
            dW = np.random.normal(0, np.sqrt(dt))

            # SDE update
            dN = drift * dt + diffusion * dW
            N_values[i + 1] = max(self.params.N_min, N + dN)

        return t_values, N_values

    def simulate_ensemble(
        self,
        N0: float,
        t_span: Tuple[float, float],
        n_trajectories: int = 100,
        n_steps: Optional[int] = None
    ) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Simulate ensemble of SDE trajectories.

        Args:
            N0: Initial population
            t_span: (t_start, t_end)
            n_trajectories: Number of trajectories
            n_steps: Number of time steps per trajectory

        Returns:
            Tuple of (time_array, list of population_arrays)
        """
        trajectories = []

        for i in range(n_trajectories):
            t_values, N_values = self.simulate_trajectory(
                N0, t_span, n_steps, random_seed=i
            )
            trajectories.append(N_values)

        return t_values, trajectories


class FokkerPlanckSolver:
    """
    Solver for Fokker-Planck equation.

    Derives steady-state probability density P_ss(N) from:
        ∂P/∂t = -∂/∂N[μ(N)P] + (1/2)∂²/∂N²[σ²(N)P]
    """

    def __init__(self, params: SDEParameters):
        """
        Initialize Fokker-Planck solver.

        Args:
            params: SDE parameters
        """
        self.params = params

    def compute_steady_state(
        self,
        N_grid: Optional[np.ndarray] = None,
        n_points: int = 1000
    ) -> FokkerPlanckSolution:
        """
        Compute steady-state probability density P_ss(N).

        For time-independent drift and diffusion:
            P_ss(N) ∝ exp(∫[2μ(N)/σ²(N)]dN)

        Args:
            N_grid: Population grid (default: linear from N_min to N_max)
            n_points: Number of grid points

        Returns:
            FokkerPlanckSolution with steady-state distribution
        """
        if N_grid is None:
            N_grid = np.linspace(
                self.params.N_min,
                self.params.N_max,
                n_points
            )

        # Compute integrand: 2μ(N)/σ²(N)
        integrand = np.zeros(len(N_grid))

        for i, N in enumerate(N_grid):
            drift = self.params.drift_func(N, 0)  # Assume time-independent
            diffusion = self.params.diffusion_func(N, 0)

            # Avoid division by zero
            if diffusion**2 > 1e-10:
                integrand[i] = 2 * drift / (diffusion**2)
            else:
                integrand[i] = 0

        # Integrate to get exponent
        exponent = cumulative_trapezoid(integrand, N_grid, initial=0)

        # Compute unnormalized P_ss
        P_ss_unnorm = np.exp(exponent)

        # Normalize
        norm = trapezoid(P_ss_unnorm, N_grid)
        P_ss = P_ss_unnorm / norm

        # Compute statistical moments
        mean_N = trapezoid(N_grid * P_ss, N_grid)
        mean_N2 = trapezoid(N_grid**2 * P_ss, N_grid)
        var_N = mean_N2 - mean_N**2
        std_N = np.sqrt(var_N)
        cv_N = std_N / mean_N if mean_N > 0 else 0

        return FokkerPlanckSolution(
            N_values=N_grid,
            P_ss=P_ss,
            mean_N=mean_N,
            var_N=var_N,
            std_N=std_N,
            cv_N=cv_N
        )


class SDEValidator:
    """
    Validator for SDE/Fokker-Planck predictions against experimental data.

    Gate 1.1 criterion: CV prediction within ±10% of observed CV.
    """

    def __init__(self, tolerance: float = 0.10):
        """
        Initialize validator.

        Args:
            tolerance: Relative tolerance for CV validation (default: ±10%)
        """
        self.tolerance = tolerance

    def validate_cv(
        self,
        predicted_cv: float,
        observed_cv: float
    ) -> Tuple[bool, float]:
        """
        Validate predicted CV against observed CV.

        Args:
            predicted_cv: CV from Fokker-Planck solution
            observed_cv: CV from experimental data

        Returns:
            Tuple of (passes_validation, relative_error)
        """
        if observed_cv == 0:
            return False, float('inf')

        relative_error = abs(predicted_cv - observed_cv) / observed_cv
        passes = relative_error <= self.tolerance

        return passes, relative_error

    def validate_ensemble(
        self,
        fp_solution: FokkerPlanckSolution,
        ensemble_data: List[float]
    ) -> Dict[str, any]:
        """
        Validate Fokker-Planck solution against ensemble data.

        Args:
            fp_solution: Fokker-Planck steady-state solution
            ensemble_data: List of observed population values

        Returns:
            Dictionary with validation results
        """
        # Compute observed statistics
        observed_mean = np.mean(ensemble_data)
        observed_std = np.std(ensemble_data, ddof=1)
        observed_cv = observed_std / observed_mean

        # Validate CV
        cv_passes, cv_error = self.validate_cv(
            fp_solution.cv_N,
            observed_cv
        )

        # Validate mean (±20% tolerance)
        mean_error = abs(fp_solution.mean_N - observed_mean) / observed_mean
        mean_passes = mean_error <= 0.20

        return {
            'cv_predicted': fp_solution.cv_N,
            'cv_observed': observed_cv,
            'cv_error': cv_error,
            'cv_passes': cv_passes,
            'mean_predicted': fp_solution.mean_N,
            'mean_observed': observed_mean,
            'mean_error': mean_error,
            'mean_passes': mean_passes,
            'overall_passes': cv_passes and mean_passes
        }


# ============================================================================
# PREDEFINED DRIFT/DIFFUSION MODELS
# ============================================================================

def logistic_drift(N: float, t: float, r: float = 0.1, K: float = 50.0) -> float:
    """Logistic growth drift: r*N*(1 - N/K)"""
    return r * N * (1 - N / K)


def demographic_diffusion(N: float, t: float, sigma: float = 0.1) -> float:
    """Demographic stochasticity diffusion: sigma*sqrt(N)"""
    return sigma * np.sqrt(max(0, N))


def environmental_diffusion(N: float, t: float, sigma: float = 0.1) -> float:
    """Environmental stochasticity diffusion: sigma*N"""
    return sigma * N


def linear_drift(N: float, t: float, r: float = 0.1) -> float:
    """Linear drift: r*N"""
    return r * N


def quadratic_drift(N: float, t: float, a: float = 0.1, b: float = 0.01) -> float:
    """Quadratic drift: a*N - b*N²"""
    return a * N - b * N**2


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_logistic_sde(
    r: float = 0.1,
    K: float = 50.0,
    sigma: float = 0.1,
    noise_type: str = 'demographic'
) -> SDEParameters:
    """
    Create SDE parameters for logistic growth with noise.

    Args:
        r: Intrinsic growth rate
        K: Carrying capacity
        sigma: Noise intensity
        noise_type: 'demographic' or 'environmental'

    Returns:
        SDEParameters
    """
    drift = lambda N, t: logistic_drift(N, t, r, K)

    if noise_type == 'demographic':
        diffusion = lambda N, t: demographic_diffusion(N, t, sigma)
    else:
        diffusion = lambda N, t: environmental_diffusion(N, t, sigma)

    return SDEParameters(
        drift_func=drift,
        diffusion_func=diffusion,
        N_max=K * 2,
        metadata={'r': r, 'K': K, 'sigma': sigma, 'noise_type': noise_type}
    )


if __name__ == "__main__":
    print("=" * 80)
    print("SDE/FOKKER-PLANCK FRAMEWORK - Gate 1.1")
    print("=" * 80)
    print()

    # Example: Logistic growth with demographic stochasticity
    print("Example: Logistic Growth + Demographic Noise")
    print("-" * 80)

    # Create SDE system
    params = create_logistic_sde(r=0.1, K=50.0, sigma=0.5)
    sde = SDESystem(params)
    fp = FokkerPlanckSolver(params)

    # Compute Fokker-Planck steady state
    solution = fp.compute_steady_state(n_points=500)

    print(f"\nFokker-Planck Solution:")
    print(f"  Mean population: {solution.mean_N:.2f}")
    print(f"  Standard deviation: {solution.std_N:.2f}")
    print(f"  Coefficient of variation: {solution.cv_N:.4f}")

    # Simulate ensemble for validation
    print(f"\nSimulating ensemble (100 trajectories)...")
    t_values, trajectories = sde.simulate_ensemble(
        N0=50.0,
        t_span=(0, 1000),
        n_trajectories=100
    )

    # Extract steady-state snapshot (final value of each trajectory)
    # This captures variability BETWEEN trajectories, not within
    ensemble_ss = [traj[-1] for traj in trajectories]

    # Validate
    validator = SDEValidator(tolerance=0.10)
    results = validator.validate_ensemble(solution, ensemble_ss)

    print(f"\nValidation Results:")
    print(f"  Predicted CV: {results['cv_predicted']:.4f}")
    print(f"  Observed CV: {results['cv_observed']:.4f}")
    print(f"  Relative error: {results['cv_error']*100:.2f}%")
    print(f"  CV validation: {'✓ PASS' if results['cv_passes'] else '✗ FAIL'}")
    print(f"  Overall: {'✓ PASS' if results['overall_passes'] else '✗ FAIL'}")

    print()
    print("=" * 80)
    print("✓ SDE/Fokker-Planck Framework Operational")
    print("=" * 80)
