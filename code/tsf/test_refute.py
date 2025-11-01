"""
Tests for tsf.refute() function

Validates extended horizon testing for pattern refutation.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import pytest
import numpy as np
from pathlib import Path
import json

from code.tsf.core import observe, discover, refute
from code.tsf.data import RefutationResult
from code.tsf.errors import RefutationError


class TestRefuteBasic:
    """Test basic refute() functionality."""

    def _create_test_data(
        self,
        tmp_path,
        population: list,
        experiment_id: str = "test"
    ):
        """Helper to create test observational data."""
        computed_mean = np.mean(population)
        computed_std = np.std(population, ddof=1) if len(population) > 1 else 0.0

        data = {
            "metadata": {
                "experiment_id": experiment_id,
                "pc_id": "PC001"
            },
            "timeseries": {
                "population": population,
                "time": list(range(len(population)))
            },
            "statistics": {
                "mean": computed_mean,
                "std": computed_std
            }
        }

        data_file = tmp_path / f"{experiment_id}.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        return observe(
            source=data_file,
            domain="population_dynamics",
            schema="pc001"
        )

    def test_refute_pattern_survives(self, tmp_path):
        """Test pattern that survives refutation (consistent regime)."""
        # Create training data (sustained stable)
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Create validation data (similar sustained stable)
        validation_pop = [100.0 + np.random.normal(0, 2.5) for _ in range(200)]
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        # Discover pattern
        pattern = discover(training_data, "regime_classification")

        # Refute with generous tolerance
        result = refute(
            pattern=pattern,
            horizon="10x",
            tolerance=0.2,
            validation_data=validation_data
        )

        # Should pass (both sustained stable, similar statistics)
        assert isinstance(result, RefutationResult)
        assert result.passed is True
        assert result.pattern_id == pattern.pattern_id
        assert result.horizon == "10x"
        assert result.metrics["regime_consistent"] is True

    def test_refute_pattern_fails(self, tmp_path):
        """Test pattern that fails refutation (regime change)."""
        # Create training data (sustained stable)
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Create validation data (collapse regime)
        validation_pop = [2.0 + np.random.normal(0, 0.3) for _ in range(200)]
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        # Discover pattern
        pattern = discover(training_data, "regime_classification")

        # Refute
        result = refute(
            pattern=pattern,
            horizon="10x",
            tolerance=0.1,
            validation_data=validation_data
        )

        # Should fail (regime changed)
        assert result.passed is False
        assert result.metrics["regime_consistent"] is False
        assert len(result.failures) > 0

    def test_refute_requires_validation_data(self, tmp_path):
        """Test that refutation requires validation data."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        pattern = discover(training_data, "regime_classification")

        with pytest.raises(RefutationError) as exc_info:
            refute(
                pattern=pattern,
                horizon="10x",
                tolerance=0.1,
                validation_data=None
            )

        assert "validation data required" in str(exc_info.value).lower()

    def test_refute_invalid_horizon(self, tmp_path):
        """Test error handling for invalid horizon."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")

        with pytest.raises(RefutationError) as exc_info:
            refute(
                pattern=pattern,
                horizon="invalid",
                tolerance=0.1,
                validation_data=validation_data
            )

        assert "unknown horizon" in str(exc_info.value).lower()

    def test_refute_invalid_tolerance(self, tmp_path):
        """Test error handling for invalid tolerance."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")

        with pytest.raises(RefutationError) as exc_info:
            refute(
                pattern=pattern,
                horizon="10x",
                tolerance=1.5,  # > 1.0
                validation_data=validation_data
            )

        assert "tolerance must be in" in str(exc_info.value).lower()


class TestRefutationMetrics:
    """Test refutation metrics calculation."""

    def _create_test_data(self, tmp_path, population, experiment_id):
        """Helper to create test observational data."""
        computed_mean = np.mean(population)
        computed_std = np.std(population, ddof=1) if len(population) > 1 else 0.0

        data = {
            "metadata": {"experiment_id": experiment_id, "pc_id": "PC001"},
            "timeseries": {"population": population, "time": list(range(len(population)))},
            "statistics": {"mean": computed_mean, "std": computed_std}
        }

        data_file = tmp_path / f"{experiment_id}.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        return observe(source=data_file, domain="population_dynamics", schema="pc001")

    def test_mean_deviation_calculation(self, tmp_path):
        """Test mean deviation calculation."""
        # Training: mean=100
        training_pop = [100.0] * 100
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Validation: mean=110 (10% deviation)
        validation_pop = [110.0] * 100
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "10x", tolerance=0.15, validation_data=validation_data)

        # Mean deviation should be ~0.10
        assert 0.09 <= result.metrics["mean_deviation"] <= 0.11

    def test_std_deviation_calculation(self, tmp_path):
        """Test relative std deviation calculation."""
        # Training: low variability
        training_pop = [100.0 + np.random.normal(0, 1) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Validation: high variability
        validation_pop = [100.0 + np.random.normal(0, 20) for _ in range(100)]
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "10x", tolerance=0.25, validation_data=validation_data)

        # Should have high std deviation
        assert result.metrics["std_deviation"] > 0.1

    def test_all_metrics_present(self, tmp_path):
        """Test that all required metrics are present."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "10x", tolerance=0.1, validation_data=validation_data)

        required_metrics = [
            "mean_deviation",
            "std_deviation",
            "regime_consistent",
            "mean_within_tolerance",
            "std_within_tolerance",
            "original_mean",
            "validation_mean",
            "original_relative_std",
            "validation_relative_std"
        ]

        for metric in required_metrics:
            assert metric in result.metrics, f"Missing metric: {metric}"


class TestRefutationFailures:
    """Test refutation failure detection."""

    def _create_test_data(self, tmp_path, population, experiment_id):
        """Helper to create test observational data."""
        computed_mean = np.mean(population)
        computed_std = np.std(population, ddof=1) if len(population) > 1 else 0.0

        data = {
            "metadata": {"experiment_id": experiment_id, "pc_id": "PC001"},
            "timeseries": {"population": population, "time": list(range(len(population)))},
            "statistics": {"mean": computed_mean, "std": computed_std}
        }

        data_file = tmp_path / f"{experiment_id}.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        return observe(source=data_file, domain="population_dynamics", schema="pc001")

    def test_regime_inconsistency_failure(self, tmp_path):
        """Test failure detection for regime inconsistency."""
        # Training: sustained
        training_pop = [100.0] * 100
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Validation: collapse
        validation_pop = [2.0] * 100
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "10x", tolerance=0.1, validation_data=validation_data)

        assert result.passed is False
        assert any(f["type"] == "regime_inconsistency" for f in result.failures)

    def test_mean_deviation_failure(self, tmp_path):
        """Test failure detection for mean deviation."""
        # Training: mean=100
        training_pop = [100.0] * 100
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Validation: mean=150 (50% deviation)
        validation_pop = [150.0] * 100
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "10x", tolerance=0.1, validation_data=validation_data)

        assert result.passed is False
        assert any(f["type"] == "mean_deviation" for f in result.failures)

    def test_std_deviation_failure(self, tmp_path):
        """Test failure detection for std deviation."""
        # Training: low variability
        training_pop = [100.0 + np.random.normal(0, 1) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Validation: very high variability
        validation_pop = [100.0 + 50 * np.sin(i * 0.1) for i in range(100)]
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "10x", tolerance=0.05, validation_data=validation_data)

        assert result.passed is False
        assert any(f["type"] == "std_deviation" for f in result.failures)

    def test_multiple_failures(self, tmp_path):
        """Test detection of multiple simultaneous failures."""
        # Training: sustained stable
        training_pop = [100.0 + np.random.normal(0, 1) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Validation: collapse with high variability
        validation_pop = [2.0 + np.random.normal(0, 1) for _ in range(100)]
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "10x", tolerance=0.05, validation_data=validation_data)

        assert result.passed is False
        # Should have regime + mean failures at minimum
        assert len(result.failures) >= 2


class TestHorizonSpecifications:
    """Test different horizon specifications."""

    def _create_test_data(self, tmp_path, population, experiment_id):
        """Helper to create test observational data."""
        computed_mean = np.mean(population)
        computed_std = np.std(population, ddof=1) if len(population) > 1 else 0.0

        data = {
            "metadata": {"experiment_id": experiment_id, "pc_id": "PC001"},
            "timeseries": {"population": population, "time": list(range(len(population)))},
            "statistics": {"mean": computed_mean, "std": computed_std}
        }

        data_file = tmp_path / f"{experiment_id}.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        return observe(source=data_file, domain="population_dynamics", schema="pc001")

    def test_10x_horizon(self, tmp_path):
        """Test 10x horizon specification."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "10x", tolerance=0.1, validation_data=validation_data)

        assert result.horizon == "10x"

    def test_extended_horizon(self, tmp_path):
        """Test extended horizon specification."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "extended", tolerance=0.1, validation_data=validation_data)

        assert result.horizon == "extended"

    def test_double_horizon(self, tmp_path):
        """Test double horizon specification."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        result = refute(pattern, "double", tolerance=0.1, validation_data=validation_data)

        assert result.horizon == "double"


class TestIntegration:
    """Integration tests for full observe → discover → refute workflow."""

    def test_full_workflow_passes(self):
        """Test full workflow with pattern that passes refutation."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")

        # Find PC001 test data
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))
        if not pc001_files or len(pc001_files) < 2:
            pytest.skip("Need at least 2 PC001 data files")

        # Use first file for training, second for validation
        training_data = observe(pc001_files[0], "population_dynamics", "pc001")
        validation_data = observe(pc001_files[0], "population_dynamics", "pc001")  # Same file

        # Discover pattern
        pattern = discover(training_data, "regime_classification")

        # Refute (should pass - same data)
        result = refute(pattern, "10x", tolerance=0.01, validation_data=validation_data)

        assert result.passed is True
        assert result.metrics["regime_consistent"] is True

    def test_full_workflow_with_pc002(self):
        """Test full workflow with PC002 data."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")

        pc002_files = list(data_dir.glob("test_pc002_pc_validation_*.json"))
        if not pc002_files:
            pytest.skip("No PC002 data files found")

        # Use same file for training and validation (should pass)
        data = observe(pc002_files[0], "population_dynamics", "pc002")

        pattern = discover(data, "regime_classification")
        result = refute(pattern, "extended", tolerance=0.01, validation_data=data)

        assert result.passed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
