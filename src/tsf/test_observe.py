"""
Tests for tsf.observe() function

Validates data loading, schema validation, and quality checks.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import pytest
import json
import numpy as np
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.tsf.core import observe
from src.tsf.data import ObservationalData
from src.tsf.errors import DataLoadError, SchemaValidationError


class TestObserveBasic:
    """Test basic observe() functionality."""

    def test_observe_valid_pc001_data(self, tmp_path):
        """Test loading valid PC001 data."""
        # Create valid PC001 data file
        population = [100.0 + i for i in range(100)]
        computed_mean = np.mean(population)
        computed_std = np.std(population, ddof=1)
        computed_cv = computed_std / computed_mean

        data = {
            "metadata": {
                "experiment_id": "test_001",
                "pc_id": "PC001",
                "domain": "population_dynamics",
                "parameters": {"growth_rate": 0.05}
            },
            "timeseries": {
                "population": population,
                "time": list(range(100))
            },
            "statistics": {
                "mean": computed_mean,
                "std": computed_std,
                "cv": computed_cv
            },
            "validation": {}
        }

        data_file = tmp_path / "test_pc001.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        # Load data
        obs_data = observe(
            source=data_file,
            domain="population_dynamics",
            schema="pc001"
        )

        # Validate returned structure
        assert isinstance(obs_data, ObservationalData)
        assert obs_data.source == data_file
        assert obs_data.domain == "population_dynamics"
        assert obs_data.schema == "pc001"
        assert "population" in obs_data.timeseries
        assert len(obs_data.timeseries["population"]) == 100
        assert obs_data.metadata["experiment_id"] == "test_001"

    def test_observe_valid_pc002_data(self, tmp_path):
        """Test loading valid PC002 data."""
        population = [100.0 + 10 * np.sin(i * 0.1) for i in range(100)]
        computed_mean = np.mean(population)
        computed_std = np.std(population, ddof=1)
        computed_cv = computed_std / computed_mean

        data = {
            "metadata": {
                "experiment_id": "test_002",
                "pc_id": "PC002",
                "domain": "population_dynamics",
                "regime_type": "OSCILLATION",
                "parameters": {"frequency": 0.05}
            },
            "timeseries": {
                "population": population,
                "time": list(range(100))
            },
            "statistics": {
                "mean": computed_mean,
                "std": computed_std,
                "cv": computed_cv
            },
            "validation": {}
        }

        data_file = tmp_path / "test_pc002.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        # Load data
        obs_data = observe(
            source=data_file,
            domain="population_dynamics",
            schema="pc002"
        )

        # Validate returned structure
        assert isinstance(obs_data, ObservationalData)
        assert obs_data.schema == "pc002"
        assert obs_data.metadata["regime_type"] == "OSCILLATION"

    def test_observe_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        with pytest.raises(DataLoadError) as exc_info:
            observe(
                source="/nonexistent/path/data.json",
                domain="test",
                schema="pc001"
            )
        assert "not found" in str(exc_info.value).lower()

    def test_observe_invalid_json(self, tmp_path):
        """Test error handling for invalid JSON."""
        data_file = tmp_path / "invalid.json"
        with open(data_file, 'w') as f:
            f.write("{ invalid json }")

        with pytest.raises(DataLoadError) as exc_info:
            observe(
                source=data_file,
                domain="test",
                schema="pc001"
            )
        assert "invalid json" in str(exc_info.value).lower()


class TestSchemaValidation:
    """Test schema validation logic."""

    def test_missing_required_keys(self, tmp_path):
        """Test error when required top-level keys are missing."""
        # Missing 'timeseries' key
        data = {
            "metadata": {"experiment_id": "test"},
            "statistics": {}
        }

        data_file = tmp_path / "missing_keys.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        with pytest.raises(SchemaValidationError) as exc_info:
            observe(source=data_file, domain="test", schema="pc001")
        assert "missing required keys" in str(exc_info.value).lower()

    def test_pc001_missing_population(self, tmp_path):
        """Test PC001 schema requires 'population' timeseries."""
        data = {
            "metadata": {
                "experiment_id": "test",
                "pc_id": "PC001",
                "domain": "population_dynamics"
            },
            "timeseries": {
                "time": list(range(100))
            },
            "statistics": {"mean": 100.0, "std": 10.0}
        }

        data_file = tmp_path / "no_population.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        with pytest.raises(SchemaValidationError) as exc_info:
            observe(source=data_file, domain="population_dynamics", schema="pc001")
        assert "population" in str(exc_info.value).lower()

    def test_pc001_missing_statistics(self, tmp_path):
        """Test PC001 schema requires mean and std statistics."""
        data = {
            "metadata": {
                "experiment_id": "test",
                "pc_id": "PC001",
                "domain": "population_dynamics"
            },
            "timeseries": {
                "population": [100.0] * 100,
                "time": list(range(100))
            },
            "statistics": {}  # Missing mean and std
        }

        data_file = tmp_path / "no_stats.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        with pytest.raises(SchemaValidationError) as exc_info:
            observe(source=data_file, domain="population_dynamics", schema="pc001")
        assert "statistics" in str(exc_info.value).lower()

    def test_pc002_missing_regime_type(self, tmp_path):
        """Test PC002 schema requires 'regime_type' in metadata."""
        data = {
            "metadata": {
                "experiment_id": "test",
                "pc_id": "PC002",
                "domain": "population_dynamics"
                # Missing regime_type
            },
            "timeseries": {
                "population": [100.0] * 100,
                "time": list(range(100))
            },
            "statistics": {"mean": 100.0, "std": 0.0}
        }

        data_file = tmp_path / "no_regime.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        with pytest.raises(SchemaValidationError) as exc_info:
            observe(source=data_file, domain="population_dynamics", schema="pc002")
        assert "regime_type" in str(exc_info.value).lower()


class TestDataQuality:
    """Test data quality validation."""

    def test_inconsistent_timeseries_lengths(self, tmp_path):
        """Test error when timeseries have different lengths."""
        data = {
            "metadata": {
                "experiment_id": "test",
                "pc_id": "PC001",
                "domain": "population_dynamics"
            },
            "timeseries": {
                "population": [100.0] * 100,
                "time": list(range(50))  # Different length
            },
            "statistics": {"mean": 100.0, "std": 0.0}
        }

        data_file = tmp_path / "inconsistent.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        with pytest.raises(SchemaValidationError) as exc_info:
            observe(source=data_file, domain="population_dynamics", schema="pc001")
        assert "inconsistent lengths" in str(exc_info.value).lower()

    def test_nan_values_rejected(self, tmp_path):
        """Test error when timeseries contain NaN values."""
        data = {
            "metadata": {
                "experiment_id": "test",
                "pc_id": "PC001",
                "domain": "population_dynamics"
            },
            "timeseries": {
                "population": [100.0, float('nan'), 100.0],
                "time": [0, 1, 2]
            },
            "statistics": {"mean": 100.0, "std": 0.0}
        }

        data_file = tmp_path / "nan_values.json"
        with open(data_file, 'w') as f:
            json.dump(data, f, allow_nan=True)

        with pytest.raises(SchemaValidationError) as exc_info:
            observe(source=data_file, domain="population_dynamics", schema="pc001")
        assert "nan" in str(exc_info.value).lower()

    def test_inf_values_rejected(self, tmp_path):
        """Test error when timeseries contain Inf values."""
        data = {
            "metadata": {
                "experiment_id": "test",
                "pc_id": "PC001",
                "domain": "population_dynamics"
            },
            "timeseries": {
                "population": [100.0, float('inf'), 100.0],
                "time": [0, 1, 2]
            },
            "statistics": {"mean": 100.0, "std": 0.0}
        }

        data_file = tmp_path / "inf_values.json"
        with open(data_file, 'w') as f:
            json.dump(data, f, allow_nan=True)

        with pytest.raises(SchemaValidationError) as exc_info:
            observe(source=data_file, domain="population_dynamics", schema="pc001")
        assert "inf" in str(exc_info.value).lower()

    def test_statistics_consistency_check(self, tmp_path):
        """Test statistics consistency verification."""
        # Create data with inconsistent statistics
        population = [100.0 + i for i in range(100)]
        correct_mean = np.mean(population)
        incorrect_mean = correct_mean + 100.0  # Way off

        data = {
            "metadata": {
                "experiment_id": "test",
                "pc_id": "PC001",
                "domain": "population_dynamics"
            },
            "timeseries": {
                "population": population,
                "time": list(range(100))
            },
            "statistics": {
                "mean": incorrect_mean,
                "std": np.std(population, ddof=1)
            }
        }

        data_file = tmp_path / "inconsistent_stats.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        with pytest.raises(SchemaValidationError) as exc_info:
            observe(source=data_file, domain="population_dynamics", schema="pc001")
        assert "inconsistent" in str(exc_info.value).lower()
        assert "mean" in str(exc_info.value).lower()


class TestObserveIntegration:
    """Integration tests with real PC validation data."""

    def test_load_real_pc001_data(self):
        """Test loading real PC001 validation data."""
        # Use test data created by pc_data_exporter.py
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")

        # Find test PC001 file
        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))
        if not pc001_files:
            pytest.skip("No test PC001 data files found")

        # Load first file
        obs_data = observe(
            source=pc001_files[0],
            domain="population_dynamics",
            schema="pc001"
        )

        # Validate structure
        assert obs_data.domain == "population_dynamics"
        assert obs_data.schema == "pc001"
        assert "population" in obs_data.timeseries
        assert len(obs_data.timeseries["population"]) > 0
        # Accept both formats for statistics
        assert ("mean" in obs_data.statistics or "mean_population" in obs_data.statistics)
        assert ("std" in obs_data.statistics or "std_population" in obs_data.statistics)

    def test_load_real_pc002_data(self):
        """Test loading real PC002 validation data."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")

        # Find test PC002 file
        pc002_files = list(data_dir.glob("test_pc002_pc_validation_*.json"))
        if not pc002_files:
            pytest.skip("No test PC002 data files found")

        # Load first file
        obs_data = observe(
            source=pc002_files[0],
            domain="population_dynamics",
            schema="pc002"
        )

        # Validate structure
        assert obs_data.domain == "population_dynamics"
        assert obs_data.schema == "pc002"
        assert "regime_type" in obs_data.metadata
        assert "population" in obs_data.timeseries

    def test_skip_validation(self, tmp_path):
        """Test that validation can be skipped."""
        # Create data with inconsistent stats (would fail validation)
        data = {
            "metadata": {
                "experiment_id": "test",
                "pc_id": "PC001",
                "domain": "population_dynamics"
            },
            "timeseries": {
                "population": [100.0] * 100,
                "time": list(range(100))
            },
            "statistics": {
                "mean": 999.0,  # Incorrect
                "std": 999.0     # Incorrect
            }
        }

        data_file = tmp_path / "skip_validation.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        # Should succeed with validate=False
        obs_data = observe(
            source=data_file,
            domain="population_dynamics",
            schema="pc001",
            validate=False
        )

        assert isinstance(obs_data, ObservationalData)
        assert obs_data.statistics["mean"] == 999.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
