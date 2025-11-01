#!/usr/bin/env python3
"""
Test Suite for SDE/Fokker-Planck Framework
===========================================

Validates Gate 1.1 implementation:
- SDE trajectory simulation
- Fokker-Planck steady-state computation
- CV prediction accuracy (±10% tolerance)
- Ensemble validation

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.sde_fokker_planck import (
    SDEParameters,
    SDESystem,
    FokkerPlanckSolver,
    FokkerPlanckSolution,
    SDEValidator,
    create_logistic_sde,
    logistic_drift,
    demographic_diffusion,
    environmental_diffusion,
    linear_drift,
    quadratic_drift
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def simple_sde_params():
    """Simple linear SDE with constant diffusion."""
    return SDEParameters(
        drift_func=lambda N, t: 0.1 * N,
        diffusion_func=lambda N, t: 0.5,
        N_min=0.1,
        N_max=100.0
    )


@pytest.fixture
def logistic_sde_params():
    """Logistic growth with demographic noise."""
    return create_logistic_sde(r=0.1, K=50.0, sigma=0.5, noise_type='demographic')


@pytest.fixture
def sde_system(logistic_sde_params):
    """SDE system instance."""
    return SDESystem(logistic_sde_params)


@pytest.fixture
def fp_solver(logistic_sde_params):
    """Fokker-Planck solver instance."""
    return FokkerPlanckSolver(logistic_sde_params)


@pytest.fixture
def validator():
    """SDE validator with ±10% tolerance."""
    return SDEValidator(tolerance=0.10)


# ============================================================================
# SDE SYSTEM TESTS
# ============================================================================

class TestSDESystem:
    """Test SDE trajectory simulation."""

    def test_initialization(self, simple_sde_params):
        """Test SDE system initialization."""
        sde = SDESystem(simple_sde_params)
        assert sde.params == simple_sde_params

    def test_simulate_trajectory_basic(self, sde_system):
        """Test single trajectory simulation."""
        t_values, N_values = sde_system.simulate_trajectory(
            N0=25.0,
            t_span=(0, 100),
            n_steps=1000,
            random_seed=42
        )

        assert len(t_values) == 1001
        assert len(N_values) == 1001
        assert N_values[0] == 25.0
        assert all(N_values >= sde_system.params.N_min)

    def test_simulate_trajectory_reproducibility(self, sde_system):
        """Test trajectory reproducibility with same seed."""
        t1, N1 = sde_system.simulate_trajectory(
            N0=25.0,
            t_span=(0, 100),
            n_steps=1000,
            random_seed=42
        )

        t2, N2 = sde_system.simulate_trajectory(
            N0=25.0,
            t_span=(0, 100),
            n_steps=1000,
            random_seed=42
        )

        np.testing.assert_array_equal(N1, N2)

    def test_simulate_trajectory_minimum_bound(self, sde_system):
        """Test that population never goes below N_min."""
        t_values, N_values = sde_system.simulate_trajectory(
            N0=1.0,
            t_span=(0, 50),
            n_steps=500,
            random_seed=123
        )

        assert all(N_values >= sde_system.params.N_min)

    def test_simulate_ensemble(self, sde_system):
        """Test ensemble simulation."""
        t_values, trajectories = sde_system.simulate_ensemble(
            N0=25.0,
            t_span=(0, 100),
            n_trajectories=10,
            n_steps=1000
        )

        assert len(trajectories) == 10
        assert all(len(traj) == 1001 for traj in trajectories)
        assert all(traj[0] == 25.0 for traj in trajectories)

    def test_ensemble_variability(self, sde_system):
        """Test that ensemble shows stochastic variability."""
        t_values, trajectories = sde_system.simulate_ensemble(
            N0=25.0,
            t_span=(0, 100),
            n_trajectories=20,
            n_steps=1000
        )

        # Final values should show variance
        final_values = [traj[-1] for traj in trajectories]
        cv = np.std(final_values) / np.mean(final_values)

        assert cv > 0  # Some variability
        assert cv < 0.5  # Not too much (system should settle near K)


# ============================================================================
# FOKKER-PLANCK SOLVER TESTS
# ============================================================================

class TestFokkerPlanckSolver:
    """Test Fokker-Planck steady-state computation."""

    def test_initialization(self, logistic_sde_params):
        """Test Fokker-Planck solver initialization."""
        solver = FokkerPlanckSolver(logistic_sde_params)
        assert solver.params == logistic_sde_params

    def test_compute_steady_state_basic(self, fp_solver):
        """Test steady-state computation."""
        solution = fp_solver.compute_steady_state(n_points=500)

        assert isinstance(solution, FokkerPlanckSolution)
        assert len(solution.N_values) == 500
        assert len(solution.P_ss) == 500

        # Check normalization
        dN = solution.N_values[1] - solution.N_values[0]
        total_prob = np.sum(solution.P_ss) * dN
        np.testing.assert_almost_equal(total_prob, 1.0, decimal=2)

    def test_steady_state_statistics(self, fp_solver):
        """Test statistical moments from steady-state."""
        solution = fp_solver.compute_steady_state(n_points=1000)

        # Mean should be positive
        assert solution.mean_N > 0

        # Variance should be positive
        assert solution.var_N > 0

        # Standard deviation should match variance
        np.testing.assert_almost_equal(
            solution.std_N,
            np.sqrt(solution.var_N),
            decimal=10
        )

        # CV should be well-defined
        expected_cv = solution.std_N / solution.mean_N
        np.testing.assert_almost_equal(solution.cv_N, expected_cv, decimal=10)

    def test_logistic_mean_near_carrying_capacity(self, fp_solver):
        """Test that logistic growth settles near K."""
        solution = fp_solver.compute_steady_state(n_points=1000)

        # Carrying capacity from params
        K = fp_solver.params.metadata['K']

        # Mean should be close to K (within 20%)
        assert abs(solution.mean_N - K) / K < 0.20

    def test_custom_grid(self, fp_solver):
        """Test steady-state with custom N grid."""
        custom_grid = np.linspace(1, 80, 800)
        solution = fp_solver.compute_steady_state(N_grid=custom_grid)

        assert len(solution.N_values) == 800
        np.testing.assert_array_equal(solution.N_values, custom_grid)

    def test_probability_density_properties(self, fp_solver):
        """Test P_ss is a valid probability density."""
        solution = fp_solver.compute_steady_state(n_points=1000)

        # All probabilities non-negative
        assert all(solution.P_ss >= 0)

        # Integrates to 1
        total_prob = np.trapz(solution.P_ss, solution.N_values)
        np.testing.assert_almost_equal(total_prob, 1.0, decimal=2)


# ============================================================================
# VALIDATOR TESTS
# ============================================================================

class TestSDEValidator:
    """Test SDE/Fokker-Planck validation."""

    def test_initialization(self):
        """Test validator initialization."""
        validator = SDEValidator(tolerance=0.10)
        assert validator.tolerance == 0.10

    def test_validate_cv_pass(self, validator):
        """Test CV validation passing case."""
        passes, error = validator.validate_cv(
            predicted_cv=0.15,
            observed_cv=0.16
        )

        assert passes
        assert error < 0.10

    def test_validate_cv_fail(self, validator):
        """Test CV validation failing case."""
        passes, error = validator.validate_cv(
            predicted_cv=0.15,
            observed_cv=0.25
        )

        assert not passes
        assert error > 0.10

    def test_validate_cv_exact_match(self, validator):
        """Test CV validation with exact match."""
        passes, error = validator.validate_cv(
            predicted_cv=0.20,
            observed_cv=0.20
        )

        assert passes
        assert error == 0.0

    def test_validate_cv_zero_observed(self, validator):
        """Test CV validation with zero observed (edge case)."""
        passes, error = validator.validate_cv(
            predicted_cv=0.15,
            observed_cv=0.0
        )

        assert not passes
        assert error == float('inf')

    def test_validate_ensemble_pass(self, validator, fp_solver):
        """Test ensemble validation passing case."""
        # Compute Fokker-Planck solution
        solution = fp_solver.compute_steady_state(n_points=500)

        # Generate ensemble data matching prediction
        np.random.seed(42)
        ensemble_data = np.random.normal(
            loc=solution.mean_N,
            scale=solution.std_N,
            size=100
        )

        results = validator.validate_ensemble(solution, ensemble_data)

        assert results['cv_passes']
        assert results['cv_error'] < 0.10

    def test_validate_ensemble_statistics(self, validator, fp_solver):
        """Test ensemble validation computes correct statistics."""
        solution = fp_solver.compute_steady_state(n_points=500)

        # Generate ensemble with known statistics
        np.random.seed(123)
        ensemble_data = np.random.normal(loc=50.0, scale=5.0, size=200)

        results = validator.validate_ensemble(solution, ensemble_data)

        # Check observed statistics
        observed_mean = np.mean(ensemble_data)
        observed_std = np.std(ensemble_data, ddof=1)
        observed_cv = observed_std / observed_mean

        np.testing.assert_almost_equal(
            results['cv_observed'],
            observed_cv,
            decimal=10
        )
        np.testing.assert_almost_equal(
            results['mean_observed'],
            observed_mean,
            decimal=10
        )


# ============================================================================
# DRIFT/DIFFUSION MODEL TESTS
# ============================================================================

class TestDriftDiffusionModels:
    """Test predefined drift and diffusion functions."""

    def test_logistic_drift(self):
        """Test logistic growth drift."""
        # At N=0, growth is zero
        assert logistic_drift(0, 0, r=0.1, K=50) == 0

        # At N=K, growth is zero
        assert logistic_drift(50, 0, r=0.1, K=50) == 0

        # At N=K/2, growth is maximal
        drift_half = logistic_drift(25, 0, r=0.1, K=50)
        assert drift_half > 0

        # Below K, growth is positive
        assert logistic_drift(20, 0, r=0.1, K=50) > 0

        # Above K, growth is negative
        assert logistic_drift(60, 0, r=0.1, K=50) < 0

    def test_demographic_diffusion(self):
        """Test demographic stochasticity ~ sqrt(N)."""
        # Zero at N=0
        assert demographic_diffusion(0, 0, sigma=0.1) == 0

        # Proportional to sqrt(N)
        diff_10 = demographic_diffusion(10, 0, sigma=0.1)
        diff_40 = demographic_diffusion(40, 0, sigma=0.1)

        expected_ratio = np.sqrt(40 / 10)
        actual_ratio = diff_40 / diff_10

        np.testing.assert_almost_equal(actual_ratio, expected_ratio, decimal=10)

    def test_environmental_diffusion(self):
        """Test environmental stochasticity ~ N."""
        # Zero at N=0
        assert environmental_diffusion(0, 0, sigma=0.1) == 0

        # Proportional to N
        diff_10 = environmental_diffusion(10, 0, sigma=0.1)
        diff_30 = environmental_diffusion(30, 0, sigma=0.1)

        expected_ratio = 30 / 10
        actual_ratio = diff_30 / diff_10

        np.testing.assert_almost_equal(actual_ratio, expected_ratio, decimal=10)

    def test_linear_drift(self):
        """Test linear drift."""
        assert linear_drift(0, 0, r=0.1) == 0
        assert linear_drift(10, 0, r=0.1) == 1.0
        assert linear_drift(20, 0, r=0.1) == 2.0

    def test_quadratic_drift(self):
        """Test quadratic drift."""
        # At N=0, drift is zero
        assert quadratic_drift(0, 0, a=0.1, b=0.01) == 0

        # Linear term dominates for small N
        drift_small = quadratic_drift(5, 0, a=0.1, b=0.01)
        assert drift_small > 0

        # Quadratic term dominates for large N
        drift_large = quadratic_drift(20, 0, a=0.1, b=0.01)
        assert drift_large < quadratic_drift(10, 0, a=0.1, b=0.01)


# ============================================================================
# UTILITY FUNCTION TESTS
# ============================================================================

class TestUtilityFunctions:
    """Test utility functions."""

    def test_create_logistic_sde_demographic(self):
        """Test logistic SDE creation with demographic noise."""
        params = create_logistic_sde(
            r=0.1,
            K=50.0,
            sigma=0.5,
            noise_type='demographic'
        )

        assert isinstance(params, SDEParameters)
        assert params.metadata['r'] == 0.1
        assert params.metadata['K'] == 50.0
        assert params.metadata['sigma'] == 0.5
        assert params.metadata['noise_type'] == 'demographic'
        assert params.N_max == 100.0  # K * 2

    def test_create_logistic_sde_environmental(self):
        """Test logistic SDE creation with environmental noise."""
        params = create_logistic_sde(
            r=0.2,
            K=30.0,
            sigma=0.3,
            noise_type='environmental'
        )

        assert params.metadata['noise_type'] == 'environmental'
        assert params.N_max == 60.0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for full SDE/Fokker-Planck workflow."""

    def test_gate_1_1_validation_workflow(self):
        """Test complete Gate 1.1 validation workflow."""
        # Create logistic SDE system
        params = create_logistic_sde(r=0.1, K=50.0, sigma=0.5)
        sde = SDESystem(params)
        fp = FokkerPlanckSolver(params)

        # Compute analytical solution
        solution = fp.compute_steady_state(n_points=500)

        # Simulate ensemble
        t_values, trajectories = sde.simulate_ensemble(
            N0=50.0,
            t_span=(0, 1000),
            n_trajectories=100,
            n_steps=10000
        )

        # Extract steady-state snapshot (final value of each trajectory)
        # This captures the variability BETWEEN trajectories, not within
        ensemble_ss = [traj[-1] for traj in trajectories]

        # Validate
        validator = SDEValidator(tolerance=0.10)
        results = validator.validate_ensemble(solution, ensemble_ss)

        # Gate 1.1 criterion: ±10% CV accuracy
        assert results['cv_passes']
        assert results['cv_error'] < 0.10
        assert results['overall_passes']

    def test_reproducibility_with_seed(self):
        """Test full workflow reproducibility."""
        params = create_logistic_sde(r=0.1, K=50.0, sigma=0.3)

        # Run 1
        sde1 = SDESystem(params)
        t1, traj1 = sde1.simulate_trajectory(
            N0=25.0,
            t_span=(0, 100),
            random_seed=999
        )

        # Run 2 (same seed)
        sde2 = SDESystem(params)
        t2, traj2 = sde2.simulate_trajectory(
            N0=25.0,
            t_span=(0, 100),
            random_seed=999
        )

        np.testing.assert_array_equal(traj1, traj2)

    def test_different_noise_types_yield_different_cv(self):
        """Test that demographic vs environmental noise affects CV."""
        # Demographic noise
        params_demo = create_logistic_sde(
            r=0.1, K=50.0, sigma=0.5, noise_type='demographic'
        )
        fp_demo = FokkerPlanckSolver(params_demo)
        sol_demo = fp_demo.compute_steady_state(n_points=500)

        # Environmental noise
        params_env = create_logistic_sde(
            r=0.1, K=50.0, sigma=0.5, noise_type='environmental'
        )
        fp_env = FokkerPlanckSolver(params_env)
        sol_env = fp_env.compute_steady_state(n_points=500)

        # CVs should differ
        assert sol_demo.cv_N != sol_env.cv_N


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
