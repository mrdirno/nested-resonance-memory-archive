"""
Tests for tsf.discover() function

Validates pattern discovery with regime classification.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import pytest
import numpy as np
from pathlib import Path

from code.tsf.core import observe, discover
from code.tsf.data import ObservationalData, DiscoveredPattern
from code.tsf.errors import DiscoveryError


class TestDiscoverBasic:
    """Test basic discover() functionality."""

    def test_discover_sustained_stable_regime(self):
        """Test discovery of sustained stable regime."""
        # Create sustained stable population data (high mean, low variability)
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))

        if not pc001_files:
            pytest.skip("No test PC001 data files found")

        # Load data
        data = observe(
            source=pc001_files[0],
            domain="population_dynamics",
            schema="pc001"
        )

        # Discover pattern
        pattern = discover(
            data=data,
            method="regime_classification"
        )

        # Validate pattern structure
        assert isinstance(pattern, DiscoveredPattern)
        assert pattern.method == "regime_classification"
        assert pattern.domain == "population_dynamics"
        assert "regime" in pattern.features
        assert "mean_population" in pattern.features
        assert "std_population" in pattern.features
        assert "is_sustained" in pattern.features
        assert "is_collapse" in pattern.features
        assert "is_oscillatory" in pattern.features

    def test_discover_with_custom_thresholds(self):
        """Test discovery with custom classification thresholds."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))

        if not pc001_files:
            pytest.skip("No test PC001 data files found")

        # Load data
        data = observe(
            source=pc001_files[0],
            domain="population_dynamics",
            schema="pc001"
        )

        # Discover with custom thresholds
        pattern = discover(
            data=data,
            method="regime_classification",
            parameters={
                "threshold_sustained": 50.0,
                "threshold_collapse": 5.0,
                "oscillation_threshold": 0.15
            }
        )

        # Validate thresholds were applied
        assert pattern.metadata["thresholds"]["sustained"] == 50.0
        assert pattern.metadata["thresholds"]["collapse"] == 5.0
        assert pattern.metadata["thresholds"]["oscillation"] == 0.15

    def test_discover_unknown_method(self):
        """Test error handling for unknown discovery method."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))

        if not pc001_files:
            pytest.skip("No test PC001 data files found")

        data = observe(
            source=pc001_files[0],
            domain="population_dynamics",
            schema="pc001"
        )

        with pytest.raises(DiscoveryError) as exc_info:
            discover(data=data, method="unknown_method")

        assert "unknown discovery method" in str(exc_info.value).lower()

    def test_discover_missing_population(self, tmp_path):
        """Test error when population timeseries missing."""
        # Create data without population
        import json
        data = {
            "metadata": {"experiment_id": "test", "pc_id": "PC001"},
            "timeseries": {"time": list(range(100))},
            "statistics": {"mean": 100.0, "std": 10.0}
        }

        data_file = tmp_path / "no_population.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        obs_data = observe(
            source=data_file,
            domain="test",
            schema="pc001",
            validate=False  # Skip validation to test discovery error
        )

        with pytest.raises(DiscoveryError) as exc_info:
            discover(data=obs_data, method="regime_classification")

        assert "population" in str(exc_info.value).lower()


class TestRegimeClassification:
    """Test regime classification logic."""

    def _create_test_data(
        self,
        tmp_path,
        population: list,
        experiment_id: str = "test"
    ) -> ObservationalData:
        """Helper to create test observational data."""
        import json

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

    def test_classify_sustained_stable(self, tmp_path):
        """Test classification of sustained stable regime."""
        # High mean, low variability
        population = [100.0 + np.random.normal(0, 2) for _ in range(100)]

        data = self._create_test_data(tmp_path, population, "sustained_stable")
        pattern = discover(data=data, method="regime_classification")

        assert pattern.features["regime"] == "SUSTAINED_STABLE"
        assert pattern.features["is_sustained"] is True
        assert pattern.features["is_collapse"] is False
        assert pattern.features["is_oscillatory"] is False

    def test_classify_sustained_oscillatory(self, tmp_path):
        """Test classification of sustained oscillatory regime."""
        # High mean, high variability
        population = [50.0 + 30 * np.sin(i * 0.1) for i in range(100)]

        data = self._create_test_data(tmp_path, population, "sustained_oscillatory")
        pattern = discover(data=data, method="regime_classification")

        assert pattern.features["regime"] == "SUSTAINED_OSCILLATORY"
        assert pattern.features["is_sustained"] is True
        assert pattern.features["is_collapse"] is False
        assert pattern.features["is_oscillatory"] is True

    def test_classify_collapse(self, tmp_path):
        """Test classification of collapse regime."""
        # Low mean population
        population = [2.0 + np.random.normal(0, 0.3) for _ in range(100)]

        data = self._create_test_data(tmp_path, population, "collapse")
        pattern = discover(data=data, method="regime_classification")

        assert pattern.features["regime"] == "COLLAPSE"
        assert pattern.features["is_sustained"] is False
        assert pattern.features["is_collapse"] is True

    def test_classify_bistable(self, tmp_path):
        """Test classification of bistable regime."""
        # Medium mean, low variability
        population = [7.0 + np.random.normal(0, 0.5) for _ in range(100)]

        data = self._create_test_data(tmp_path, population, "bistable")
        pattern = discover(data=data, method="regime_classification")

        assert pattern.features["regime"] == "BISTABLE"
        assert pattern.features["is_sustained"] is False
        assert pattern.features["is_collapse"] is False
        assert pattern.features["is_oscillatory"] is False

    def test_classify_bistable_oscillatory(self, tmp_path):
        """Test classification of bistable oscillatory regime."""
        # Medium mean, high variability
        population = [7.0 + 3 * np.sin(i * 0.2) for i in range(100)]

        data = self._create_test_data(tmp_path, population, "bistable_oscillatory")
        pattern = discover(data=data, method="regime_classification")

        assert pattern.features["regime"] == "BISTABLE_OSCILLATORY"
        assert pattern.features["is_sustained"] is False
        assert pattern.features["is_collapse"] is False
        assert pattern.features["is_oscillatory"] is True


class TestDiscoverFeatures:
    """Test discovered pattern features."""

    def test_pattern_features_complete(self):
        """Test that all expected features are present."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))

        if not pc001_files:
            pytest.skip("No test PC001 data files found")

        data = observe(
            source=pc001_files[0],
            domain="population_dynamics",
            schema="pc001"
        )

        pattern = discover(data=data, method="regime_classification")

        # Check all required features present
        required_features = [
            "regime",
            "mean_population",
            "std_population",
            "min_population",
            "max_population",
            "relative_std",
            "cv_population",
            "is_sustained",
            "is_collapse",
            "is_oscillatory"
        ]

        for feature in required_features:
            assert feature in pattern.features, f"Missing feature: {feature}"

    def test_pattern_metadata_complete(self):
        """Test that pattern metadata is complete."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))

        if not pc001_files:
            pytest.skip("No test PC001 data files found")

        data = observe(
            source=pc001_files[0],
            domain="population_dynamics",
            schema="pc001"
        )

        pattern = discover(data=data, method="regime_classification")

        # Check metadata
        assert "source" in pattern.metadata
        assert "thresholds" in pattern.metadata
        assert "sustained" in pattern.metadata["thresholds"]
        assert "collapse" in pattern.metadata["thresholds"]
        assert "oscillation" in pattern.metadata["thresholds"]

    def test_feature_values_reasonable(self):
        """Test that feature values are within reasonable ranges."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))

        if not pc001_files:
            pytest.skip("No test PC001 data files found")

        data = observe(
            source=pc001_files[0],
            domain="population_dynamics",
            schema="pc001"
        )

        pattern = discover(data=data, method="regime_classification")

        # Check value ranges
        assert pattern.features["mean_population"] >= 0
        assert pattern.features["std_population"] >= 0
        assert pattern.features["min_population"] >= 0
        assert pattern.features["max_population"] >= pattern.features["min_population"]
        assert pattern.features["relative_std"] >= 0
        assert pattern.features["cv_population"] >= 0


class TestIntegration:
    """Integration tests for observe + discover workflow."""

    def test_full_workflow_pc001(self):
        """Test full observe → discover workflow with PC001 data."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))

        if not pc001_files:
            pytest.skip("No test PC001 data files found")

        # Step 1: Observe
        data = observe(
            source=pc001_files[0],
            domain="population_dynamics",
            schema="pc001"
        )

        # Step 2: Discover
        pattern = discover(
            data=data,
            method="regime_classification"
        )

        # Validate end-to-end
        assert pattern.domain == data.domain
        assert str(data.source) in pattern.metadata["source"]
        assert pattern.features["mean_population"] > 0
        assert pattern.features["regime"] in [
            "SUSTAINED_STABLE",
            "SUSTAINED_OSCILLATORY",
            "COLLAPSE",
            "BISTABLE",
            "BISTABLE_OSCILLATORY"
        ]

    def test_full_workflow_pc002(self):
        """Test full observe → discover workflow with PC002 data."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")
        pc002_files = list(data_dir.glob("test_pc002_pc_validation_*.json"))

        if not pc002_files:
            pytest.skip("No test PC002 data files found")

        # Step 1: Observe
        data = observe(
            source=pc002_files[0],
            domain="population_dynamics",
            schema="pc002"
        )

        # Step 2: Discover
        pattern = discover(
            data=data,
            method="regime_classification"
        )

        # Validate
        assert pattern.domain == "population_dynamics"
        assert pattern.features["regime"] in [
            "SUSTAINED_STABLE",
            "SUSTAINED_OSCILLATORY",
            "COLLAPSE",
            "BISTABLE",
            "BISTABLE_OSCILLATORY"
        ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
